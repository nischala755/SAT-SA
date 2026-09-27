'use client';
import {useState} from 'react';
import {api,display,Row} from '../../lib/workbench';
type FileRow={filename:string;table:string;content:string;mapping:Record<string,string>};
const tables=['cses','assets','alerts','cases','investigation_events','escalations'];
export function Ingestion({token,onJob}:{token:string;onJob:(job:Row)=>void}) {
  const [files,setFiles]=useState<FileRow[]>([]); const [id,setId]=useState('submission-001');
  const [preview,setPreview]=useState<Row|null>(null); const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
  const [mapping,setMapping]=useState<Record<number,string>>({});
  async function submit(commit=false) {
    setBusy(true);setError('');
    try {
      const mapped=files.map((f,i)=>({...f,mapping:JSON.parse(mapping[i]||'{}')}));
      const result=await api<Row>(commit?'ingestion':'ingestion/preview',token,{dataset_id:id,files:mapped});
      if(commit)onJob(result);else setPreview(result);
    }catch(e){setError(String(e));}finally{setBusy(false);}
  }
  return <section><h2>Data ingestion</h2><p>Upload CSV or JSON exports, map source columns to canonical fields, preview validation, then publish an immutable version. Maximum 2 MB per file and 10,000 total rows. Supply CSE metadata with the evidence tables.</p>
    <label>Dataset version <input value={id} onChange={e=>{setId(e.target.value);setPreview(null);}}/></label>
    <label>Structured files <input type="file" multiple accept=".csv,.json" onChange={async e=>{setError('');setPreview(null);const selected=Array.from(e.target.files??[]);if(selected.some(f=>f.size>2000000)){setError('Each file must be at most 2 MB.');return;}setFiles(await Promise.all(selected.map(async f=>({filename:f.name,table:tables.find(t=>f.name.startsWith(t))??'alerts',content:await f.text(),mapping:{}}))));}}/></label>
    {files.map((f,i)=><fieldset key={i}><legend>{f.filename}</legend><label>Evidence table <select value={f.table} onChange={e=>{setFiles(files.map((x,j)=>j===i?{...x,table:e.target.value}:x));setPreview(null);}}>{tables.map(t=><option key={t}>{t}</option>)}</select></label>
    <label>Column mapping JSON (source to canonical) <textarea value={mapping[i]??'{}'} onChange={e=>{setMapping({...mapping,[i]:e.target.value});setPreview(null);}}/></label>
    <details><summary>Source preview</summary><pre>{f.content.slice(0,2000)}</pre></details></fieldset>)}
    <button disabled={busy||!files.length} onClick={()=>void submit()}>Validate and preview</button>{' '}
    <button disabled={busy||preview?.valid!==true} onClick={()=>void submit(true)}>Import immutable dataset</button>
    {error&&<p role="alert" className="error">{error}</p>}
    {preview&&<><h3>Validation summary</h3><p>Valid: {display(preview.valid)} · Submitted: {display(preview.submitted)} · Rejected: {display(preview.rejected)}</p>
    <details open><summary>Errors, missingness and normalized preview</summary><pre>{JSON.stringify(preview,null,2)}</pre></details></>}
  </section>;
}
