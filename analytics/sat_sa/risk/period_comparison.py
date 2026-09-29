"""Descriptive comparison of immutable, non-overlapping assessment runs."""
from datetime import datetime


def _date(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def _context(result):
    run = result['run']
    period = run['assessment_period']
    days = (_date(period['end']) - _date(period['start'])).total_seconds() / 86400
    if days <= 0:
        raise ValueError('Assessment period must have positive duration')
    return {key: run[key] for key in ('run_id', 'dataset_id', 'dataset_hash')} | {'period': period, 'days': days}


def _metrics(entity, days):
    return {
        'alerts': entity['alerts'], 'cases': entity['cases'],
        'alerts_per_30_days': round(entity['alerts'] * 30 / days, 4),
        'cases_per_30_days': round(entity['cases'] * 30 / days, 4),
        'high_priority_indicators': entity['high_priority'],
        'submitted_closure_completeness': entity['completeness'],
    }


def compare_runs(baseline, current):
    """Compare rates and completeness; changes never imply improvement or failure."""
    before, after = _context(baseline), _context(current)
    if before['run_id'] == after['run_id'] or _date(before['period']['end']) > _date(after['period']['start']):
        raise ValueError('Choose different, chronological, non-overlapping assessment runs')
    old = {e['cse_id']: e for e in baseline['entities']}
    new = {e['cse_id']: e for e in current['entities']}
    rows = []
    for cse_id in sorted(old.keys() | new.keys()):
        left, right = old.get(cse_id), new.get(cse_id)
        reason = None
        if left is None or right is None:
            reason = 'Entity absent from one submitted assessment'
        elif (left['name'], left['sector'], left['peer_group']) != (right['name'], right['sector'], right['peer_group']):
            reason = 'Entity identity, sector or peer cohort changed; direct comparison unavailable'
        b = _metrics(left, before['days']) if left else None
        c = _metrics(right, after['days']) if right else None
        rows.append({
            'cse_id': cse_id, 'name': (right or left)['name'], 'comparable': reason is None,
            'unavailable_reason': reason, 'baseline': b, 'current': c,
            'alert_rate_change_per_30_days': round(c['alerts_per_30_days'] - b['alerts_per_30_days'], 4) if reason is None else None,
            'case_rate_change_per_30_days': round(c['cases_per_30_days'] - b['cases_per_30_days'], 4) if reason is None else None,
            'interpretation': 'Descriptive evidence change; examine source records and submission completeness before drawing a supervisory conclusion.' if reason is None else 'Analysis unavailable due to insufficient comparable evidence.',
        })
    return {'baseline': before, 'current': after, 'entities': rows,
            'methodology': 'Counts are normalized to 30-day rates using assessment-window duration. Indicator counts and closure completeness are descriptive; they are not control-effectiveness scores.'}
