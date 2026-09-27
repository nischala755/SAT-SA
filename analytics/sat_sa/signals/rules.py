"""Versioned observable predicates, independent of HTTP, storage and labels."""
from collections import Counter, defaultdict
from datetime import timedelta

def duration(start,end): return (end-start).total_seconds()/60 if start and end else None

def fast_closure(alerts,cfg):
    return [a for a in alerts if a.severity in cfg['expected_escalation_severities'] and a.closure_timestamp and duration(a.timestamp,a.closure_timestamp)<=cfg['fast_minutes']]

def weak_investigation(cases,events,cfg):
    counts=Counter(e.case_id for e in events)
    return [c for c in cases if c.severity in cfg['expected_escalation_severities'] and c.closed_at and counts[c.case_id]<cfg['minimum_investigation_events']]

def missing_escalation(alerts,escalations,cfg):
    known={e.alert_id for e in escalations}
    return [a for a in alerts if (a.escalation_required is True or a.severity in cfg['expected_escalation_severities']) and a.closure_timestamp and a.alert_id not in known and a.escalation_timestamp is None]

def recurrence(alerts,cfg):
    groups=defaultdict(list); result=[]
    for a in alerts:
        if a.asset_id: groups[(a.asset_id,a.alert_category)].append(a)
    for rows in groups.values():
        rows.sort(key=lambda a:(a.timestamp,a.alert_id)); left=0; selected={}
        for right,row in enumerate(rows):
            while rows[left].timestamp<row.timestamp-timedelta(days=cfg['recurrence_days']): left+=1
            if right-left+1>=cfg['recurrence_count']:
                for item in rows[left:right+1]: selected[item.alert_id]=item
        result.extend(selected.values())
    return sorted(result,key=lambda a:a.alert_id)

def closure_bursts(cases,cfg):
    groups=defaultdict(list)
    for c in cases:
        if c.closed_at: groups[c.closed_at.replace(second=0,microsecond=0)].append(c)
    return [c for rows in groups.values() if len(rows)>=cfg['burst_count'] for c in rows]

def repeated_templates(cases,cfg):
    groups=defaultdict(list)
    for c in cases:
        if c.closure_reason and c.investigation_steps_count is not None and c.investigation_steps_count<cfg['minimum_investigation_events']:
            groups[c.closure_reason].append(c)
    return [c for rows in groups.values() if len(rows)>=cfg['minimum_sample'] for c in rows]
