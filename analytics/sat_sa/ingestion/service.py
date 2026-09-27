"""Bounded structured submission normalization; no labels or arbitrary URL fetching."""
import csv
import io
import json
from pathlib import PurePath
from pydantic import ValidationError
from sat_sa.repositories.relationships import validate_records
from sat_sa_contracts.models import RECORD_MODELS

MAX_FILE_BYTES=2_000_000
MAX_ROWS=10000


def _normalize(submission, batch):
    files=submission.get('files',[])
    if not 1 <= len(files) <= 12:
        raise ValueError('Supply between 1 and 12 structured files')
    records={name:[] for name in RECORD_MODELS}
    errors=[]; columns=[]; count=0
    for file in files:
        kind=file['table']; name=file['filename']; content=file['content']; mapping=file.get('mapping',{})
        if kind not in RECORD_MODELS or PurePath(name).name!=name or '/' in name or '\\' in name or len(name)>120:
            raise ValueError('Invalid evidence table or source filename')
        if len(content.encode())>MAX_FILE_BYTES:
            raise ValueError('File exceeds 2 MB prototype limit')
        if name.lower().endswith('.json'):
            rows=json.loads(content)
            if not isinstance(rows,list): raise ValueError('JSON must be an array of records')
        elif name.lower().endswith('.csv'):
            reader=csv.DictReader(io.StringIO(content))
            if len(reader.fieldnames or []) != len(set(reader.fieldnames or [])):
                raise ValueError('Duplicate CSV columns')
            rows=list(reader)
        else:
            raise ValueError('Only CSV and JSON exports are accepted')
        count+=len(rows)
        if count>MAX_ROWS: raise ValueError('Submission exceeds 10,000 row prototype limit')
        columns.append({'filename':name,'table':kind,'columns':list(rows[0]) if rows and isinstance(rows[0],dict) else [],'rows':len(rows)})
        for index,row in enumerate(rows,1):
            try:
                if not isinstance(row,dict): raise ValueError('Record must be an object')
                converted={}
                for key,value in row.items():
                    target=mapping.get(key,key)
                    if target in converted: raise ValueError('Column mapping collides')
                    if value=='': value=None
                    # CSV primitive/nested values follow their canonical JSON representations.
                    if isinstance(value,str) and target not in ('cse_id','alert_id','case_id','asset_id','event_id','escalation_id'):
                        if value in ('true','false','null') or value.startswith(('{','[')) or target.endswith('_count') or target in ('notes_length','investigation_duration','investigation_steps_count'):
                            try: value=json.loads(value)
                            except json.JSONDecodeError: pass
                    converted[target]=value
                converted['provenance']={'source_file':name,'source_record':str(index),'ingestion_batch':batch,'transformation_version':'1.0.0'}
                records[kind].append(RECORD_MODELS[kind].model_validate(converted))
            except (ValidationError,ValueError,TypeError) as exc:
                errors.append({'filename':name,'row':index,'message':str(exc)[:1000]})
    if not errors:
        try: records=validate_records(records)
        except ValueError as exc: errors.append({'filename':'relationships','row':0,'message':str(exc)})
    return records,errors,columns,count


def preview_submission(submission):
    records,errors,columns,count=_normalize(submission,'preview')
    missing={kind:{field:sum(getattr(r,field) is None for r in rows) for field in RECORD_MODELS[kind].model_fields if field!='provenance'} for kind,rows in records.items()}
    return {'valid':not errors,'submitted':count,'accepted':sum(map(len,records.values())),
            'rejected':sum(e['row']>0 for e in errors),'errors':errors[:100],'error_count':len(errors),
            'columns':columns,'missingness':missing,'preview':{k:[r.model_dump(mode='json') for r in v[:5]] for k,v in records.items()}}


def normalize_submission(submission,batch):
    records,errors,_,_=_normalize(submission,batch)
    if errors: raise ValueError(f'Submission rejected: {len(errors)} validation errors; {errors[0]["message"]}')
    return records
