"""Finite deduplicated samples with transparent additive priority factors."""
def prioritize(signals):
    samples={}
    for s in signals:
        for ref in s['evidence_references']:
            key=(ref['cse_id'],ref['record_type'],ref['record_id'])
            row=samples.setdefault(key,{'cse_id':key[0],'record_type':key[1],'record_id':key[2],'signals':[], 'references':[ref],
                'confidence':s['confidence'],'objective':'Inspect referenced evidence and document contextual explanation or concern.'})
            row['signals'].append(s)
    result=[]
    for row in samples.values():
        ss=row.pop('signals'); rules={s['rule_id'] for s in ss}
        row['signal_ids']=[s['signal_id'] for s in ss]; row['reasons']=[s['name'] for s in ss]
        factors={'severity':max({'high':30,'critical':40,'medium':15,'low':5,'informational':0}[s['severity']] for s in ss),
                 'corroboration':min(30,10*(len(ss)-1)), 'evidence_strength':10 if any(s['confidence']!='limited' for s in ss) else 0,
                 'recurrence':10 if 'recurrence' in rules else 0,'peer_deviation':10 if 'peer_deviation' in rules else 0,
                 'novelty':0}
        row.update(contributions=factors,priority=sum(factors.values()),novelty_reason='No previous assessed run comparison; novelty contributes zero')
        result.append(row)
    return sorted(result,key=lambda r:(-r['priority'],r['cse_id'],r['record_type'],r['record_id']))
