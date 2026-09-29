from fastapi.testclient import TestClient
from sat_sa_api.main import create_app
from sat_sa.config.settings import Settings


def test_comparison_endpoint_uses_persisted_runs(tmp_path):
    with TestClient(create_app(Settings(storage_root=tmp_path))) as client:
        repo = client.app.state.repository
        for run_id, start, end, alerts in [
            ('baseline', '2024-01-01T00:00:00Z', '2024-01-31T00:00:00Z', 30),
            ('current', '2025-01-01T00:00:00Z', '2025-03-02T00:00:00Z', 60),
        ]:
            repo.save_result(run_id, {
                'run': {'run_id': run_id, 'dataset_id': run_id, 'dataset_hash': run_id,
                        'assessment_period': {'start': start, 'end': end}},
                'entities': [{'cse_id': 'C1', 'name': 'Entity', 'sector': 'energy',
                              'peer_group': 'energy-critical', 'alerts': alerts,
                              'cases': alerts // 2, 'high_priority': 1, 'completeness': 1}],
                'signals': [], 'trends': [], 'queue': [], 'unavailable': [],
            })
        response = client.get('/api/v1/period-comparison', params={
            'baseline_run_id': 'baseline', 'current_run_id': 'current'})
        assert response.status_code == 200
        assert response.json()['entities'][0]['alert_rate_change_per_30_days'] == 0
        assert client.get('/api/v1/reports/current').json()['status'] == 'requires_human_review'
        assert client.get('/api/v1/period-comparison', params={
            'baseline_run_id': 'missing', 'current_run_id': 'current'}).status_code == 404
