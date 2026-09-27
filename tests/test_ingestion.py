import json
from pathlib import Path
import pytest
from sat_sa.ingestion.service import preview_submission, normalize_submission

def submission():
    from sat_sa.repositories.parquet_evidence import ParquetEvidenceRepository
    repo=ParquetEvidenceRepository(Path('data/sample'))
    rows=repo.read_records('demo','cses','CSE-01')
    return {'files':[{'table':'cses','filename':'entities.json','content':json.dumps([r.model_dump(mode='json') for r in rows]),'mapping':{}}]}

def test_json_csv_and_provenance():
    result=normalize_submission(submission(),'import-1')
    assert result['cses'][0].provenance.ingestion_batch=='import-1'
    assert result['alerts']==[]
    assert preview_submission(submission())['valid']

def test_rejected_and_unknown_table():
    data=submission(); data['files'][0]['content']='[{"cse_id":"only"}]'
    preview=preview_submission(data)
    assert not preview['valid'] and preview['rejected']==1
    with pytest.raises(ValueError): normalize_submission(data,'bad')
    data['files'][0]['table']='ground_truth'
    with pytest.raises(ValueError): preview_submission(data)

def test_bad_format_and_bounds():
    data=submission(); data['files'][0]['content']='x'*2_000_001
    with pytest.raises(ValueError): preview_submission(data)

def test_csv_mapping_and_missing_evidence():
    data=submission()
    data['files'].append({'table':'assets','filename':'inventory.csv','mapping':{'entity':'cse_id'},
       'content':'entity,asset_id,criticality,environment,system_type,monitoring_expected\nCSE-01,A1,critical,prod,server,true\n'})
    result=normalize_submission(data,'mapped')
    assert result['assets'][0].monitoring_expected is True
    assert result['assets'][0].monitoring_source is None

def test_cross_entity_reference_rejected():
    data=submission()
    data['files'].append({'table':'assets','filename':'a.json','mapping':{},'content':json.dumps([{
       'cse_id':'OTHER','asset_id':'A1','criticality':'critical','environment':'prod','system_type':'server','monitoring_expected':True}])})
    assert not preview_submission(data)['valid']
