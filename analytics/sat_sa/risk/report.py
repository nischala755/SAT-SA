"""Bounded, evidence-backed examiner report from one immutable run."""
from sat_sa.risk.overview import summarize


def build_report(result, decisions):
    signals = sorted(result['signals'], key=lambda item: (item['cse_id'], item['signal_id']))
    selected = []
    for signal in signals[:50]:
        selected.append({key: value for key, value in signal.items() if key != 'evidence_references'} |
                        {'evidence_references': signal['evidence_references'][:10],
                         'references_total': len(signal['evidence_references'])})
    return {
        'title': 'SAT-SA supervisory assessment report',
        'status': 'requires_human_review',
        'caution': 'Analytical indicators are review prompts, not findings of non-compliance. Missing evidence does not prove control failure.',
        'run': result['run'],
        'overview': summarize(result),
        'entities': result['entities'],
        'signals': selected,
        'signals_total': len(signals),
        'review_samples': result['queue'][:20],
        'review_samples_total': len(result['queue']),
        'unavailable_analyses': result['unavailable'],
        'review_decisions': decisions,
        'scope': 'First 50 signals, first 10 references per signal, and first 20 suggested samples. Use the evidence API for complete records.',
    }
