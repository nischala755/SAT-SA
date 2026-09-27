"""Exercise a prepared Compose deployment, including real outage and restart.

Run only against this project's synthetic demo: temporarily stops its API.
Every subprocess command, exit code and output is retained in artifacts.
"""
import json
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "artifacts/verification/container-checks.jsonl"


def command(argv):
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=240)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps({"command": argv, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}) + "\n")
    if result.returncode:
        raise RuntimeError(f"{argv} failed ({result.returncode}): {result.stderr}\n{result.stdout}")
    return result.stdout.strip()


def get_json(url):
    with urlopen(url, timeout=10) as response:
        return json.load(response)


def main():
    before = get_json("http://127.0.0.1:3001/api/status")
    assert before["ok"] and before["health"]["registered_datasets"] == 1
    # DNS-independent TCP probes; the browser tests separately inspect resource origins.
    python_probe = """import socket,json
results=[]
for host in ['1.1.1.1','8.8.8.8']:
 try:
  connection=socket.create_connection((host,443),timeout=2); connection.close(); results.append({'host':host,'blocked':False})
 except OSError as error:
  results.append({'host':host,'blocked':True,'reason':type(error).__name__})
print(json.dumps(results))
assert all(r['blocked'] for r in results), 'External egress unexpectedly available'
"""
    node_probe = """const net=require('node:net'); Promise.all(['1.1.1.1','8.8.8.8'].map(host=>new Promise(resolve=>{const s=net.connect({host,port:443});s.setTimeout(2000);s.once('connect',()=>{s.destroy();resolve({host,blocked:false})});s.once('error',e=>resolve({host,blocked:true,reason:e.code}));s.once('timeout',()=>{s.destroy();resolve({host,blocked:true,reason:'timeout'})})}))).then(results=>{console.log(JSON.stringify(results));process.exit(results.every(r=>r.blocked)?0:1)})"""
    snapshot_code = """import json
from pathlib import Path
from sat_sa.repositories.workflow import WorkflowRepository
from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository
with WorkflowRepository(Path('/var/lib/sat-sa/metadata.duckdb')) as r:
 r.initialize()
 print(json.dumps({'dataset':r.get_dataset('demo').model_dump(mode='json'),'audit':[a.model_dump(mode='json') for a in r.list_audit()],'runs':r.runs(),'reviews':r.decisions(),'verified_manifest':ParquetEvidenceRepository(Path('/var/lib/sat-sa/evidence')).load_manifest('demo').model_dump(mode='json')}))
"""
    snapshot_cmd = ["docker", "compose", "run", "--rm", "--no-deps", "--entrypoint", "python", "api", "-c", snapshot_code]
    command(["docker", "compose", "stop", "api"])
    try:
        try:
            get_json("http://127.0.0.1:3001/api/status")
            raise AssertionError("Proxy incorrectly reported success with API stopped")
        except HTTPError as error:
            assert error.code == 503
            assert json.load(error)["ok"] is False
        command(["node", "scripts/check_outage.mjs", "http://127.0.0.1:3001"])
        snapshot_before = json.loads(command(snapshot_cmd))
    finally:
        command(["docker", "compose", "up", "--pull", "never", "--no-build", "--wait"])
    assert get_json("http://127.0.0.1:3001/api/status") == before
    command(["docker", "compose", "stop", "api"])
    try:
        snapshot_after = json.loads(command(snapshot_cmd))
    finally:
        command(["docker", "compose", "up", "--pull", "never", "--no-build", "--wait"])
    assert snapshot_before == snapshot_after, "Evidence or audit changed across restart"
    assert sum(a['action']=='dataset_registered' for a in snapshot_after['audit']) == 1
    isolated = ["docker", "compose", "-f", "compose.yaml", "-f", "compose.offline.yaml"]
    try:
        command(isolated + ["up", "--pull", "never", "--no-build", "--wait"])
        network = json.loads(command(["docker", "network", "inspect", "sat-sa-offline-verification"]))[0]
        assert network["Internal"] is True
        api_probe = json.loads(command(isolated + ["exec", "-T", "api", "python", "-c", python_probe]))
        web_probe = json.loads(command(isolated + ["exec", "-T", "web", "node", "-e", node_probe]))
        http_probe = """(async()=>{
const base='http://127.0.0.1:3000';
const html=await (await fetch(base)).text();
if(!html.includes('SAT-SA')) throw Error('Shell missing');
const assets=[...new Set([...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(m=>m[1]))];
if(assets.length<2) throw Error('Bundled assets missing');
for(const asset of assets){
 if(!asset.startsWith('/') || asset.startsWith('//')) throw Error('Nonlocal asset: '+asset);
 const r=await fetch(base+asset); if(!r.ok) throw Error('Asset unavailable: '+asset);
 await r.arrayBuffer();
}
const health=await (await fetch(base+'/api/status')).json();
if(!health.ok || health.health.registered_datasets!==1) throw Error('Backend unavailable');
const call=async(path,body)=>{const r=await fetch(base+'/api/service/'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});const value=await r.json();if(!r.ok)throw Error(JSON.stringify(value));return value;};
let job=await call('analytics/run',{dataset_id:'demo'});
for(let i=0;i<120 && ['queued','running'].includes(job.status);i++){await new Promise(r=>setTimeout(r,500));job=await call('jobs/'+job.job_id);}
if(job.status!=='completed')throw Error('Offline analytics failed: '+JSON.stringify(job));
const signals=await call('signals?run_id='+job.run_id);
if(!signals.total)throw Error('No computed indicators');
const signal=await call('signals/'+signals.items[0].signal_id+'?run_id='+job.run_id);
const ref=signal.evidence_references[0];
const evidence=await call('evidence?'+new URLSearchParams({dataset_id:ref.dataset_id,cse_id:ref.cse_id,table:ref.record_type,record_id:ref.record_id}));
if(evidence.total!==1)throw Error('Source trace failed');
await call('reviews',{run_id:job.run_id,signal_id:signal.signal_id,cse_id:signal.cse_id,outcome:'further_investigation',note:'Isolated-network verification on synthetic evidence'});
const audit=await call('audit');if(!audit.items.some(e=>e.action==='review_recorded'))throw Error('Review audit absent');
console.log(JSON.stringify({shell:true,assets:assets.length,frontend_backend:true,health,offline_analytics:true,evidence_trace:true,human_review:true,run_id:job.run_id}));
})().catch(e=>{console.error(e);process.exit(1)})"""
        offline_http = json.loads(command(isolated + ["exec", "-T", "web", "node", "-e", http_probe]))
    finally:
        command(["docker", "compose", "up", "--pull", "never", "--no-build", "--wait"])
    assert get_json("http://127.0.0.1:3001/api/status") == before
    report = {"internal_network": True, "api_external_probes": api_probe, "web_external_probes": web_probe,
              "offline_http_and_assets": offline_http, "default_compose_enforces_egress": False,
              "connectivity_after_denied_egress": "passed", "real_backend_outage_ui": "passed",
              "restart_persistence": "passed", "audit_events_after_restart": len(snapshot_after["audit"]),
              "dataset_hash": snapshot_after["dataset"]["dataset_hash"]}
    (ROOT / "artifacts/verification/container-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
