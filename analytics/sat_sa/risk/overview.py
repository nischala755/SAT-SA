"""Full-run aggregates independent of display pagination; no composite risk score."""
from collections import Counter

def summarize(result,sector=None):
    entities=[e for e in result['entities'] if not sector or e['sector']==sector]
    ids={e['cse_id'] for e in entities}
    signals=[s for s in result['signals'] if s['cse_id'] in ids]
    months=Counter()
    for r in result['trends']:
        if r['cse_id'] in ids: months[r['month']]+=r['alerts']
    return {'cse_count':len(entities),'alerts':sum(e['alerts'] for e in entities),'cases':sum(e['cases'] for e in entities),
            'signal_count':len(signals),'attention_distribution':dict(sorted(Counter(s['category'] for s in signals).items())),
            'evidence_gap_count':sum(s['expectation'] is not None for s in signals),
            'trends':[{'month':month,'alerts':value} for month,value in sorted(months.items())]}
