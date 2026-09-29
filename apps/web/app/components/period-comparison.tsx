'use client';
import {useState} from 'react';
import {api,display,Row} from '../../lib/workbench';

export function PeriodComparison({runs,run,token}:{runs:Row[];run:string;token:string}){
 const [baseline,setBaseline]=useState(''),[data,setData]=useState<Row|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function compare(){setError('');setBusy(true);setData(null);try{setData(await api<Row>('period-comparison?'+new URLSearchParams({baseline_run_id:baseline,current_run_id:run}),token));}catch(e){setError(String(e));}finally{setBusy(false);}}
 const rows=(data?.entities??[]) as Row[];
 return <section><h2>Assessment period comparison</h2><p>Compare separate completed submissions. Rates account for assessment-window length. A difference is a review prompt, not a determination of control effectiveness.</p>
  <div className="toolbar"><label>Earlier run <select value={baseline} onChange={e=>setBaseline(e.target.value)}><option value="">Select baseline</option>{runs.filter(r=>r.run_id!==run).map(r=><option key={String(r.run_id)} value={String(r.run_id)}>{display(r.dataset_id)} · {display((r.assessment_period as Row)?.start)}</option>)}</select></label><button disabled={!baseline||!run||busy} onClick={()=>void compare()}>Compare periods</button></div>
  {error&&<p role="alert" className="error">{error}</p>}{busy&&<p role="status">Comparing completed runs…</p>}
  {data&&<><p className="run-context">Baseline {display((data.baseline as Row)?.run_id)} ({display((data.baseline as Row)?.days)} days) → Current {display((data.current as Row)?.run_id)} ({display((data.current as Row)?.days)} days)</p><p>{display(data.methodology)}</p><div className="table-scroll"><table><thead><tr><th>CSE</th><th>Earlier alerts / 30 days</th><th>Current alerts / 30 days</th><th>Change / 30 days</th><th>Closure completeness</th><th>Interpretation</th></tr></thead><tbody>{rows.map(r=>{const before=r.baseline as Row|null,after=r.current as Row|null;return <tr key={String(r.cse_id)}><td>{display(r.cse_id)}</td><td>{display(before?.alerts_per_30_days)}</td><td>{display(after?.alerts_per_30_days)}</td><td>{display(r.alert_rate_change_per_30_days)}</td><td>{display(before?.submitted_closure_completeness)} → {display(after?.submitted_closure_completeness)}</td><td>{display(r.unavailable_reason??r.interpretation)}</td></tr>;})}</tbody></table></div></>}
 </section>;
}
