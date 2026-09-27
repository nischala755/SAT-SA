import pytest
from sat_sa.ingestion.internal import validate_endpoint,fetch_export

@pytest.mark.parametrize('url',['https://example.com/data','http://169.254.169.254/latest','http://127.0.0.1@evil.com','file:///tmp/x'])
def test_noninternal_endpoints_rejected(url):
    with pytest.raises(ValueError): validate_endpoint(url)

def test_fixed_private_endpoint_and_disabled():
    assert validate_endpoint('http://127.0.0.1:9000/export')=='http://127.0.0.1:9000/export'
    with pytest.raises(ValueError,match='disabled'): fetch_export(None)
