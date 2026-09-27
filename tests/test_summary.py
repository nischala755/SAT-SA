from pathlib import Path
import pytest
from sat_sa.assistance.summary import draft_summary, SummaryError

ROOT = Path('data/sample')

def test_scoped_summary_and_references():
    seen = []
    def transport(url, body, headers):
        seen.append((url, body, headers))
        return {'done': True, 'done_reason': 'stop', 'model': 'qwen3.5:2b', 'message': {'content': 'Review the supplied evidence.'}}
    result = draft_summary(ROOT, 'demo', 'CSE-01', 'alerts', 2, transport=transport)
    assert len(result['records']) == len(result['references']) == 2
    assert all(r['cse_id'] == 'CSE-01' for r in result['references'])
    assert result['requires_human_review'] is True
    assert seen[0][0] == 'http://127.0.0.1:11434/api/chat'
    assert 'ground_truth' not in str(seen)

@pytest.mark.parametrize('kind,limit', [('labels',1),('alerts',0),('alerts',11)])
def test_invalid_selection(kind,limit):
    with pytest.raises(ValueError): draft_summary(ROOT,'demo','CSE-01',kind,limit)

def test_mistral_requires_explicit_consent(monkeypatch):
    monkeypatch.setenv('MISTRAL_API_KEY','test-secret')
    with pytest.raises(SummaryError, match='consent'):
        draft_summary(ROOT,'demo','CSE-01','alerts',1,provider='mistral')

def test_missing_entity_and_bad_response():
    with pytest.raises(SummaryError,match='No evidence'):
        draft_summary(ROOT,'demo','unknown','alerts',1)
    with pytest.raises(SummaryError,match='incomplete'):
        draft_summary(ROOT,'demo','CSE-01','alerts',1,transport=lambda *a: {'done':False})

@pytest.mark.parametrize('response',[[],None,{'done':True,'done_reason':'stop','message':[]}])
def test_malformed_provider_is_visible(response):
    with pytest.raises(SummaryError):
        draft_summary(ROOT,'demo','CSE-01','alerts',1,transport=lambda *a:response)

def test_mistral_payload_and_secret_separation(monkeypatch):
    monkeypatch.setenv('MISTRAL_API_KEY','test-secret-not-real')
    def transport(url,body,headers):
        assert url=='https://api.mistral.ai/v1/chat/completions'
        assert headers['Authorization']=='Bearer test-secret-not-real'
        assert body['tool_choice']=='none'
        return {'model':'mistral-test','choices':[{'finish_reason':'stop','message':{'content':'Review original evidence.'}}]}
    output=draft_summary(ROOT,'demo','CSE-01','alerts',1,provider='mistral',cloud_consent=True,transport=transport)
    assert 'test-secret' not in str(output)
