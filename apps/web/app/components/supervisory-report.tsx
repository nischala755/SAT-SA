'use client';
import {useEffect,useState} from 'react';
import {api,display,Row} from '../../lib/workbench';

export function SupervisoryReport({run,token}:{run:string;token:string}){
 const [report,setReport]=useState<Row|null>(null),[error,setError]=useState('');
 useEffect(()=>{let active=true;if(!run)return;api<Row>('reports/'+encodeURIComponent(run),token).then(value=>{if(active){setReport(value);setError('');}}).catch(e=>{if(active)setError(String(e));});return()=>{active=false;};},[run,token]);
 if(!run)return <p>Complete an analytics run to prepare a report.</p>;
 const signals=(report?.signals??[]) as Row[], entities=(report?.entities??[]) as Row[], decisions=(report?.review_decisions??[]) as Row[];
 return <section className="print-report"><h2>Supervisory assessment report</h2>{error&&<p role="alert" className="error">{error}</p>}{!report&&!error&&<p role="status">Preparing evidence-backed report…</p>}{report&&<>
  <div className="report-actions"><button onClick={()=>window.print()}>Print or save as PDF</button><button onClick={()=>{const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='sat-sa-report-'+run+'.json';link.click();URL.revokeObjectURL(url);}}>Download source report JSON</button></div>
  <p className="notice">{display(report.caution)}</p><p>Run {display((report.run as Row)?.run_id)} · Dataset {display((report.run as Row)?.dataset_id)} · Hash {display((report.run as Row)?.dataset_hash)}</p>
  <h3>Assessment scope</h3><p>{display(report.scope)}</p><p>{entities.length} entities · {display(report.signals_total)} indicators · {display(report.review_samples_total)} suggested review samples · {decisions.length} recorded decisions</p>
  <h3>Entities</h3><div className="table-scroll"><table><thead><tr><th>CSE</th><th>Sector</th><th>Alerts</th><th>Cases</th><th>High-priority indicators</th><th>Closure completeness</th></tr></thead><tbody>{entities.map(e=><tr key={String(e.cse_id)}><td>{display(e.cse_id)}</td><td>{display(e.sector)}</td><td>{display(e.alerts)}</td><td>{display(e.cases)}</td><td>{display(e.high_priority)}</td><td>{display(e.completeness)}</td></tr>)}</tbody></table></div>
  <h3>Review indicators and source references</h3>{signals.map(s=><article className="report-signal" key={String(s.signal_id)}><h4>{display(s.cse_id)} · {display(s.name)}</h4><p>{display(s.observed_evidence)} Confidence: {display(s.confidence)}. Evidence records: {display(s.references_total)}.</p><p>Method: {display(s.methodology)}</p>{Boolean(s.expectation)&&<p>Expectation: {display(s.expectation)}</p>}<p>Sample references: {((s.evidence_references??[]) as Row[]).map(r=>`${r.cse_id}/${r.record_type}/${r.record_id}`).join(', ')}</p></article>)}
  <h3>Human decisions</h3>{decisions.length?decisions.map((d,i)=><p key={i}>{display(d.timestamp)} · {display(d.actor)} · {display(d.signal_id)} · {display(d.outcome)} · {display(d.note)}</p>):<p>No human decisions recorded for this run.</p>}
  <h3>Unavailable analyses</h3><p>{display(report.unavailable_analyses)}</p>
 </>}</section>;
}
