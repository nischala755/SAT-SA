"use client";

import { useCallback, useEffect, useState } from "react";
import type { StatusResult } from "../lib/status";
import Workbench from './components/workbench';

export default function Home() {
  const [result, setResult] = useState<StatusResult | null>(null);
  const [checking, setChecking] = useState(true);
  const refresh = useCallback(async () => {
    setChecking(true);
    try {
      const response = await fetch("/api/status", { cache: "no-store", signal: AbortSignal.timeout(5000) });
      const data = await response.json() as StatusResult;
      setResult(data);
    } catch {
      setResult({ ok: false, message: "Backend unavailable. Check the local API service and retry." });
    } finally { setChecking(false); }
  }, []);
  useEffect(() => { void refresh(); }, [refresh]);

  return <>
    <header><div className="brand"><h1>SAT-SA</h1><p>Supervisory Analytics Tool for SOC Assessment</p></div><span className="badge">Local synthetic demonstration</span></header>
    <main>
      <p className="eyebrow">EVIDENCE-LED SUPERVISORY EXAMINATION</p>
      <h2>System status</h2>
      <p className="intro">Submitted evidence, explainable review indicators and human supervisory decisions. All analytical results are computed from the selected dataset.</p>
      <section aria-labelledby="connection-heading" className="panel">
        <div className="panel-heading"><h3 id="connection-heading">Application connection</h3><button onClick={() => void refresh()} disabled={checking}>{checking ? "Checking…" : result?.ok ? "Refresh status" : "Retry connection"}</button></div>
        <div aria-live="polite" aria-busy={checking}>
          {checking ? <p>Checking backend and local storage…</p> : result?.ok ? <>
            <p className="connected">Backend connected</p>
            <dl><div><dt>Storage</dt><dd>{result.health.message}</dd></div><div><dt>Registered datasets</dt><dd>{result.health.registered_datasets}</dd></div><div><dt>API version</dt><dd>{result.health.software_version}</dd></div><div><dt>Environment</dt><dd>{result.health.demo_mode ? "Synthetic demo only" : "Non-demo"}</dd></div></dl>
          </> : <p role="alert" className="error">{result?.message ?? "Backend unavailable."}</p>}
        </div>
      </section>
      {result?.ok && <Workbench/>}
      <p className="notice">Analytics will identify indicators for human examination. They will not make automatic supervisory findings.</p>
    </main>
    <footer>SAT-SA prototype · Local demonstration · Indicators require human examination</footer>
  </>;
}
