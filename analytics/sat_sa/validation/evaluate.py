"""Post-run label evaluation. Never imported by signal predicates."""
import random
from sat_sa_contracts.models import RECORD_KEYS

def evaluate(signals,queue,labels,records):
    universe={(r.cse_id,k,getattr(r,RECORD_KEYS[k])) for k,rows in records.items() for r in rows}
    positives={(l['cse_id'],e['record_type'],e['record_id']) for l in labels if l['scenario']!='healthy_control' for e in l['evidence']} & universe
    predicted={(r['cse_id'],r['record_type'],r['record_id']) for s in signals for r in s['evidence_references']} & universe
    tp=len(predicted&positives); fp=len(predicted-positives); negatives=universe-positives
    n=min(20,len(queue)); top={(q['cse_id'],q['record_type'],q['record_id']) for q in queue[:n]}
    random_keys=random.Random(20260927).sample(sorted(universe),min(20,len(universe)))
    divide=lambda a,b:a/b if b else None
    refs=[r for s in signals for r in s['evidence_references']]
    hits=0; average_precision=0
    for i,q in enumerate(queue,1):
        if (q['cse_id'],q['record_type'],q['record_id']) in positives:
            hits+=1; average_precision+=hits/i
    return {'scope':'Synthetic injected-record universe; unlabelled records treated as negative for this evaluation only',
       'universe':len(universe),'labelled_positive':len(positives),'predicted_positive':len(predicted),'true_positive':tp,'false_positive':fp,
       'precision':divide(tp,len(predicted)),'recall':divide(tp,len(positives)),'false_positive_rate':divide(fp,len(negatives)),
       'coverage':divide(len(predicted),len(universe)),'precision_at_20':divide(len(top&positives),n),'recall_at_20':divide(len(top&positives),len(positives)),
       'top_n':n,'random_seed':20260927,'random_precision_at_20':divide(len(set(random_keys)&positives),len(random_keys)),
       'traceability':divide(sum((r['cse_id'],r['record_type'],r['record_id']) in universe for r in refs),len(refs)),
       'time_saved':None,'time_saved_reason':'No measured human review timings; no productivity claim',
       'ranking_quality':divide(average_precision,len(positives))}
