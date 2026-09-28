'use client';
import {useCallback,useEffect,useState,useRef} from 'react';
import {api,display,Page,Row} from '../../lib/workbench';
import {Ingestion} from './ingestion';

const views=['Overview','Entities','Review queue','Signals','Negative space','Data ingestion','Validation','Audit trail'] as const;
const categories=['detection','investigation','escalation','incident_response','security_operations','governance','operational_discipline','cyber_resilience'];
function Grid({rows,columns,action}:{rows:Row[];columns:string[];action?:(r:Row)=>React.ReactNode}) {
 return <div className="table-scroll"><table><thead><tr>{columns.map(k=><th key={k}>{k.replaceAll('_',' ')}</th>)}{action&&<th>Examine</th>}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{columns.map(k=><td key={k}>{display(r[k])}</td>)}{action&&<td>{action(r)}</td>}</tr>)}</tbody></table>{!rows.length&&<p>No records match this selection.</p>}</div>;
}
export default function Workbench({authRequired=false}:{authRequired?:boolean}){
 const loadSequence=useRef(0);
 const [referenceOffset,setReferenceOffset]=useState(0);
 const [overview,setOverview]=useState<Row|null>(null);
 const [view,setView]=useState<string>('Overview'),[token,setToken]=useState(''),[runs,setRuns]=useState<Row[]>([]),[run,setRun]=useState(''),[datasets,setDatasets]=useState<Row[]>([]),[dataset,setDataset]=useState('demo');
 const [items,setItems]=useState<Row[]>([]),[total,setTotal]=useState(0),[offset,setOffset]=useState(0),[error,setError]=useState(''),[busy,setBusy]=useState(false),[job,setJob]=useState<Row|null>(null);
 const [entity,setEntity]=useState(''),[category,setCategory]=useState(''),[sector,setSector]=useState(''),[severity,setSeverity]=useState(''),[detail,setDetail]=useState<Row|null>(null),[source,setSource]=useState<Row|null>(null);
 const [note,setNote]=useState(''),[outcome,setOutcome]=useState('further_investigation'),[saved,setSaved]=useState(''),[validation,setValidation]=useState<Row|null>(null),[profile,setProfile]=useState<Row|null>(null),[trends,setTrends]=useState<Row[]>([]),[identity,setIdentity]=useState<Row|null>(null);
 const refresh=useCallback(async()=>{try{const [r,d,person]=await Promise.all([api<Page>('analytics/runs',token),api<Page>('datasets',token),api<Row>('identity',token)]);setRuns(r.items);setDatasets(d.items);setIdentity(person);if(!run&&r.items.length)setRun(String(r.items[0].run_id));}catch(e){setError(String(e));}},[token,run]);
 useEffect(()=>{void refresh();},[refresh]);
 useEffect(()=>{if(run)return;const id=setInterval(()=>void refresh(),2000);return()=>clearInterval(id);},[run,refresh]);
 useEffect(()=>{if(!job||!['queued','running'].includes(String(job.status)))return;const id=setInterval(async()=>{try{const next=await api<Row>('jobs/'+job.job_id,token);setJob(next);if(next.status==='completed'){await refresh();if(next.run_id)setRun(String(next.run_id));}if(next.status==='failed')setError(String(next.error));}catch(e){setError(String(e));}},1000);return()=>clearInterval(id);},[job,token,refresh]);
 const load=useCallback(async()=>{
   const sequence=++loadSequence.current;
   setError('');setBusy(true);setItems([]);setValidation(null);setProfile(null);
   try{
     if(view==='Data ingestion')return;
     const query=new URLSearchParams({limit:'25',offset:String(offset)});if(run)query.set('run_id',run);
     if(entity&&['Signals','Negative space','Review queue'].includes(view))query.set('cse_id',entity);
     if(category&&view==='Signals')query.set('category',category);
     if(severity&&view==='Signals')query.set('severity',severity);
     if(sector&&['Overview','Entities'].includes(view))query.set('sector',sector);
     if(view==='Validation'){const value=await api<Row>('validation?'+query,token);if(sequence===loadSequence.current)setValidation(value);return;}
     const endpoint=view==='Audit trail'?'audit':view==='Review queue'?'review-queue':['Signals','Negative space','Entity'].includes(view)?'signals':'entities';
     if(view==='Entity')query.set('cse_id',entity);
     if(view==='Negative space')query.set('expectation_only','true');
     const response=await api<Page>(endpoint+'?'+query,token);
     if(sequence!==loadSequence.current)return;
     setItems(response.items);setTotal(response.total);
     if(view==='Entity')setProfile(await api<Row>(`entities/${entity}?run_id=${run}`,token));
     if(view==='Overview'){const summary=await api<Row>('overview?'+query,token);if(sequence===loadSequence.current){setOverview(summary);setTrends(summary.trends as Row[]);}}
   }catch(e){if(sequence===loadSequence.current)setError(String(e));}finally{if(sequence===loadSequence.current)setBusy(false);}
 },[view,run,offset,entity,category,sector,severity,token]);
 useEffect(()=>{void load();},[load]);
 function navigate(next:string){setView(next);setOffset(0);setDetail(null);setSource(null);}
 async function inspect(id:string,offset=0,selected?:Row){try{setDetail(await api<Row>(`signals/${id}?run_id=${run}&limit=25&offset=${offset}`,token));setReferenceOffset(offset);setSource(null);if(offset===0){setSaved('');setNote('');}if(selected)await openSource(selected);}catch(e){setError(String(e));}}
 async function openSource(ref:Row){try{const data=await api<Page>('evidence?'+new URLSearchParams({dataset_id:String(ref.dataset_id),cse_id:String(ref.cse_id),table:String(ref.record_type),record_id:String(ref.record_id)}),token);setSource(data.items[0]??null);}catch(e){setError(String(e));}}
 async function decide(){if(!detail)return;try{await api('reviews',token,{run_id:run,signal_id:detail.signal_id,cse_id:detail.cse_id,outcome,note});setSaved('Human decision recorded in audit trail.');}catch(e){setError(String(e));}}
 const selectedRun=runs.find(r=>r.run_id===run);
 const months=Object.entries(trends.reduce<Record<string,number>>((a,r)=>{a[String(r.month)]=(a[String(r.month)]??0)+Number(r.alerts);return a;},{}));
 return <section className="workbench" aria-label="Supervisory workspace">
  <div className="workspace-title"><h2>Supervisory workspace</h2><span className="badge">{display(identity?.actor)} · {display(identity?.role)}</span></div>
  <p className="notice">Evidence → signal → hypothesis → human examination → auditable decision. Indicators are not findings of non-compliance.</p>
  <details open={authRequired}><summary>Configured identity token (non-demo deployments)</summary><label>Bearer token <input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)}/></label><p>{authRequired?'Enter the provisioned token to load assessment data. ':''}Kept in page memory only. Roles are assigned by the backend.</p></details>
  <div className="toolbar"><label>Assessment run <select value={run} onChange={e=>{setRun(e.target.value);setOffset(0);setDetail(null);}}><option value="">No completed run</option>{runs.map(r=><option key={String(r.run_id)} value={String(r.run_id)}>{String(r.dataset_id)} · {String(r.started_at)}</option>)}</select></label>
  <label>Dataset <select value={dataset} onChange={e=>setDataset(e.target.value)}>{datasets.map(d=><option key={String(d.dataset_id)}>{String(d.dataset_id)}</option>)}</select></label>
  <button disabled={identity?.role==='reader'||['queued','running'].includes(String(job?.status))} onClick={async()=>{try{setJob(await api<Row>('analytics/run',token,{dataset_id:dataset}));}catch(e){setError(String(e));}}}>Run analytics</button><button onClick={()=>{void refresh();void load();}}>Refresh workspace</button></div>
  {selectedRun&&<p className="run-context">Period: {display((selectedRun.assessment_period as Row)?.start)} — {display((selectedRun.assessment_period as Row)?.end)} · Dataset hash: <code>{String(selectedRun.dataset_hash).slice(0,16)}</code> · Analytics {display(selectedRun.analytics_version)}</p>}
  {job&&<p role="status">{display(job.kind)} job: {display(job.status)} {job.error?display(job.error):''}</p>}
  <nav aria-label="Assessment views">{views.map(v=><button key={v} aria-current={view===v?'page':undefined} onClick={()=>navigate(v)}>{v}</button>)}</nav>
  {error&&<p role="alert" className="error">{error}</p>}{busy&&<p role="status">Loading evidence-backed results…</p>}
  {view==='Data ingestion'?<Ingestion token={token} onJob={setJob}/>:<>
  <h2>{view==='Overview'?'Supervisory overview':view==='Entity'?`Entity assessment: ${entity}`:view}</h2>
  {['Overview','Entities'].includes(view)&&<label>Sector filter <input value={sector} placeholder="All sectors; enter an exact sector name" onChange={e=>{setSector(e.target.value);setOffset(0);}}/></label>}
  {['Signals','Review queue','Negative space'].includes(view)&&<div className="toolbar"><label>CSE filter <input value={entity} placeholder="All entities" onChange={e=>{setEntity(e.target.value);setOffset(0);}}/></label>{view==='Signals'&&<><label>Signal family <select value={category} onChange={e=>{setCategory(e.target.value);setOffset(0);}}><option value="">All families</option>{categories.map(c=><option key={c}>{c}</option>)}</select></label><label>Severity <select value={severity} onChange={e=>setSeverity(e.target.value)}><option value="">All severities</option><option>high</option><option>medium</option></select></label></>}</div>}
  {view==='Overview'&&!busy&&!error&&overview&&<><div className="kpis">{[['CSEs',overview.cse_count],['Alerts',overview.alerts],['Cases',overview.cases],['Review indicators',overview.signal_count]].map(([label,value])=><div key={String(label)}><span>{display(label)}</span><strong>{display(value)}</strong></div>)}</div>
  <details><summary>Attention distribution by signal family · {display(overview.evidence_gap_count)} evidence-gap indicators</summary><Grid rows={Object.entries(overview.attention_distribution as Row).map(([family,indicators])=>({family,indicators}))} columns={['family','indicators']}/></details>
  <details open><summary>Submitted alert volume by month</summary><div className="bars">{months.map(([month,count])=><div key={month}><span>{month}</span><meter min={0} max={Math.max(...months.map(m=>m[1]),1)} value={count}/><span>{count}</span></div>)}</div></details></>}
  {['Overview','Entities'].includes(view)&&<Grid rows={items} columns={['cse_id','sector','peer_group','alerts','cases','signal_count','high_priority','completeness']} action={r=><button aria-label={'Assess '+r.cse_id} onClick={()=>{setEntity(String(r.cse_id));navigate('Entity');}}>Assess</button>}/>}
  {profile&&<><p>{display(profile.name)} · {display(profile.peer_group)}</p><details open><summary>Peer and historical comparison; unavailable analyses</summary><pre>{JSON.stringify({peer:profile.peer,historical_closure_minutes:profile.historical_closure_minutes,current_closure_minutes:profile.current_closure_minutes,unavailable:profile.unavailable},null,2)}</pre></details></>}
  {['Signals','Negative space','Entity'].includes(view)&&<Grid rows={items} columns={['name','category','severity','evidence_count','confidence','observed_evidence']} action={r=><button aria-label={'Inspect '+r.name} onClick={()=>void inspect(String(r.signal_id))}>Inspect evidence</button>}/>}
  {view==='Review queue'&&<Grid rows={items} columns={['cse_id','record_type','record_id','priority','reasons','contributions','confidence']} action={r=><button onClick={()=>void inspect(String((r.signal_ids as string[])[0]),0,(r.references as Row[])[0])}>Review evidence</button>}/>}
  {view==='Audit trail'&&<Grid rows={items} columns={['timestamp','actor','role','action','object_id','details']}/>}
  {view==='Validation'&&validation&&<><p>Synthetic evaluation is separate from human-reviewed outcomes. Unlabelled synthetic records are treated as negatives only within this benchmark.</p>{validation.unavailable_reason&&<p>{display(validation.unavailable_reason)}</p>}<Grid rows={Object.entries((validation.synthetic??{}) as Row).map(([metric,value])=>({metric,value}))} columns={['metric','value']}/><h3>Human review outcomes</h3><pre>{JSON.stringify(validation.human_review,null,2)}</pre></>}
  {view!=='Validation'&&<div className="pagination"><button disabled={offset===0} onClick={()=>setOffset(Math.max(0,offset-25))}>Previous page</button><span>{total?offset+1:0}–{Math.min(offset+25,total)} of {total}</span><button disabled={offset+25>=total} onClick={()=>setOffset(offset+25)}>Next page</button></div>}
  </>}
  {detail&&<aside className="evidence-panel" aria-label="Evidence drawer"><button onClick={()=>setDetail(null)}>Close evidence</button><h2>Evidence and supervisory hypothesis</h2><h3>{display(detail.name)}</h3>
  <dl>{['observed_evidence','inferred_signal','supervisory_hypothesis','methodology','confidence','data_completeness','completeness_basis','evidence_count'].map(k=><div key={k}><dt>{k.replaceAll('_',' ')}</dt><dd>{display(detail[k])}</dd></div>)}</dl>
  <details><summary>Calculation, thresholds and expectations</summary><pre>{JSON.stringify({calculation:detail.calculation,thresholds:detail.thresholds,expectation:detail.expectation,peer:detail.peer},null,2)}</pre></details>
  <p>Source references {referenceOffset+1}–{Math.min(referenceOffset+25,Number(detail.evidence_count))} of {display(detail.evidence_count)}</p><Grid rows={(detail.evidence_references??[]) as Row[]} columns={['cse_id','record_type','record_id']} action={r=><button aria-label={'Open source '+r.record_id} onClick={()=>void openSource(r)}>Open source</button>}/>
  <div className="pagination"><button disabled={referenceOffset===0} onClick={()=>void inspect(String(detail.signal_id),Math.max(0,referenceOffset-25))}>Previous evidence page</button><button disabled={referenceOffset+25>=Number(detail.evidence_count)} onClick={()=>void inspect(String(detail.signal_id),referenceOffset+25)}>Next evidence page</button></div>
  {source&&<details open><summary>Source record</summary><pre>{JSON.stringify(source,null,2)}</pre></details>}
  <h3>Human examination</h3><label>Review outcome <select value={outcome} onChange={e=>setOutcome(e.target.value)}>{['accepted','dismissed','explained','confirmed_concern','false_positive','insufficient_evidence','further_investigation'].map(o=><option key={o}>{o}</option>)}</select></label>
  <label>Supervisory note <textarea value={note} maxLength={4000} onChange={e=>setNote(e.target.value)}/></label><button disabled={identity?.role==='reader'} onClick={()=>void decide()}>Record human decision</button>{saved&&<p role="status">{saved}</p>}
  </aside>}
 </section>;
}
