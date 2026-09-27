"""Deterministic supervisory indicators. Never reads ground-truth labels."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from statistics import median
from sat_sa_contracts.models import RECORD_KEYS
from sat_sa.repositories.parquet_evidence import canonical_json
from sat_sa.signals import rules
from sat_sa.negative_space.expectations import monitoring_gaps, category_gaps
from sat_sa.peer_analysis.statistics import peer_stats
from sat_sa.config.engine import EngineConfig,load_engine

VERSION='1.0.0'

def configuration():
    return load_engine()

def analyse(records, config=None, dataset_id='demo'):
    cfg=EngineConfig.model_validate(config).model_dump() if config is not None else configuration(); signals=[]; unavailable=[]; entities=[]; trends=[]
    # Explicit entity partition prevents colliding record IDs from crossing CSEs.
    grouped={c.cse_id:{k:[r for r in rows if r.cse_id==c.cse_id] for k,rows in records.items()} for c in records['cses']}
    closure={cid:median(ds) if (ds:=[rules.duration(a.timestamp,a.closure_timestamp) for a in d['alerts'] if a.closure_timestamp and a.severity in cfg['expected_escalation_severities']]) else None for cid,d in grouped.items()}
    for cse in sorted(records['cses'],key=lambda c:c.cse_id):
        cid=cse.cse_id; d=grouped[cid]; alerts=d['alerts']; cases=d['cases']; assets=d['assets']
        comparable=[c.cse_id for c in records['cses'] if c.cse_id!=cid and (c.sector,c.peer_group,c.criticality,c.entity_size)==(cse.sector,cse.peer_group,cse.criticality,cse.entity_size)]
        peers=peer_stats(closure[cid],[closure[p] for p in comparable if closure[p] is not None],cfg['minimum_peers']) if closure[cid] is not None else {'available':False,'reason':'No closed high-severity alerts','count':0}
        missing=sum(a.closure_timestamp is None for a in alerts)
        completeness=(len(alerts)-missing)/len(alerts) if alerts else 0
        monthly=Counter(a.timestamp.strftime('%Y-%m') for a in alerts)
        for month,count in sorted(monthly.items()): trends.append({'cse_id':cid,'month':month,'alerts':count})
        midpoint=cse.assessment_period.start+(cse.assessment_period.end-cse.assessment_period.start)/2
        historical=[rules.duration(a.timestamp,a.closure_timestamp) for a in alerts if a.timestamp<midpoint and a.closure_timestamp]
        current=[rules.duration(a.timestamp,a.closure_timestamp) for a in alerts if a.timestamp>=midpoint and a.closure_timestamp]
        entity={'cse_id':cid,'name':cse.name,'sector':cse.sector,'peer_group':cse.peer_group,'period':cse.assessment_period.model_dump(mode='json'),
            'alerts':len(alerts),'cases':len(cases),'assets':len(assets),'completeness':completeness,'peer':peers,
            'historical_closure_minutes':median(historical) if historical else None,'current_closure_minutes':median(current) if current else None}
        entities.append(entity)

        def emit(rule,name,category,rows,kind,denominator,method,severity='medium',expectation=None):
            if not rows: return
            unique=sorted({getattr(r,RECORD_KEYS[kind]):r for r in rows}.values(),key=lambda r:getattr(r,RECORD_KEYS[kind]))
            sufficient=denominator>=cfg['minimum_sample']
            references=[{'dataset_id':dataset_id,'cse_id':cid,'record_type':kind,'record_id':getattr(r,RECORD_KEYS[kind]),'provenance':r.provenance.model_dump()} for r in unique]
            signals.append({'signal_id':hashlib.sha256(f'{dataset_id}:{cid}:{rule}'.encode()).hexdigest()[:24], 'rule_id':rule,'cse_id':cid,'name':name,
                'category':category,'severity':severity,'description':'Review indicator; no determination of non-compliance.',
                'signal_strength':'high' if len(unique)/max(1,denominator)>.5 else 'medium','confidence':'medium' if sufficient else 'limited',
                'data_completeness':completeness,'evidence_count':len(unique),'methodology':method,'thresholds':cfg,
                'observed_evidence':f'{len(unique)} of {denominator} eligible {kind} match the documented predicate.',
                'inferred_signal':name,'supervisory_hypothesis':'Check source records and seek context before determining whether this is a supervisory concern.',
                'evidence_references':references,'calculation_version':VERSION,'calculation':{'numerator':len(unique),'denominator':denominator,'ratio':len(unique)/max(1,denominator)},
                'expectation':expectation,'peer':peers,'historical_closure_minutes':entity['historical_closure_minutes']})

        fast=rules.fast_closure(alerts,cfg)
        emit('fast_closure','High-severity alerts closed unusually quickly','detection',fast,'alerts',sum(a.severity in cfg['expected_escalation_severities'] and a.closure_timestamp is not None for a in alerts),f"Closed within {cfg['fast_minutes']} minutes; short closure alone does not establish weak investigation.",'high')
        weak=rules.weak_investigation(cases,d['investigation_events'],cfg)
        emit('weak_investigation','Limited supporting investigation activity','investigation',weak,'cases',len(cases),f"Closed high-severity cases with fewer than {cfg['minimum_investigation_events']} submitted events.",'high')
        emit('template_repetition','Repeated minimal investigation patterns','investigation',rules.repeated_templates(cases,cfg),'cases',len(cases),'Identical closure reason plus low reported step count repeated at least minimum_sample times.')
        escalation=rules.missing_escalation(alerts,d['escalations'],cfg)
        emit('missing_escalation','Expected escalation evidence absent','escalation',escalation,'alerts',len(alerts),'Closed alerts requiring escalation or matching configured severities, without a timestamp or submitted escalation record.','high',{'expected':'Escalation record or timestamp for eligible alerts','observed':len(alerts)-len(escalation),'gap':len(escalation),'source':'Configured severity/record expectation'})
        repeated=rules.recurrence(alerts,cfg)
        emit('recurrence','Recurring activity on the same asset','incident_response',repeated,'alerts',len(alerts),f"At least {cfg['recurrence_count']} alerts of a category on an asset within {cfg['recurrence_days']} days. Review remediation context.")
        unresolved=[c for c in cases if not c.closed_at and (cse.assessment_period.end-c.opened_at).days>=cfg['long_case_days']]
        emit('long_cases','Long-running unresolved cases','incident_response',unresolved,'cases',len(cases),f"Unclosed at assessment end and open at least {cfg['long_case_days']} days.")
        investigators=Counter(c.investigator for c in cases if c.investigator)
        dominant=investigators.most_common(1)
        if dominant and len(cases)>=cfg['minimum_sample'] and dominant[0][1]/len(cases)>=cfg['concentration_ratio']:
            emit('workload_concentration','Concentrated investigator workload','security_operations',[c for c in cases if c.investigator==dominant[0][0]],'cases',len(cases),'Assignment share exceeds configured concentration_ratio. Descriptive; no inference about conduct.')
        governance=[c for c in cases if c.closed_at and (c.root_cause is None or c.remediation_status is None)]
        emit('missing_fields','Closed cases missing supporting fields','governance',governance,'cases',len(cases),'Root-cause or remediation field absent in a closed case; investigate submission completeness.')
        emit('closure_bursts','Closure activity clustered in the same minute','operational_discipline',rules.closure_bursts(cases,cfg),'cases',len(cases),f"At least {cfg['burst_count']} case closures in the same minute. Reporting workflow can explain this pattern.")
        if not assets:
            unavailable.append({'cse_id':cid,'rule':'monitoring_gap','reason':'Asset inventory not supplied; coverage analysis unavailable'})
        else:
            expected,gaps=monitoring_gaps(assets,alerts)
            emit('monitoring_gap','Expected critical-asset activity absent','cyber_resilience',gaps,'assets',len(expected),'Declared monitoring expectation and no submitted alerts during the period. Alert absence does not establish a monitoring failure.','high',{'expected':len(expected),'observed':len(expected)-len(gaps),'gap':len(gaps),'source':'Critical inventory assets with monitoring_expected=true','sufficiency':'Alert activity is a proxy, not a monitoring heartbeat'})
        absent=category_gaps(alerts,cfg['expected_categories'])
        if absent:
            emit('category_gap','Expected detection categories absent','detection',[cse],'cses',1,'Configured category presence expectation; applicability requires human confirmation.',expectation={'expected':cfg['expected_categories'],'observed':sorted({a.alert_category for a in alerts}),'gap':absent,'source':'Configuration'})
        volumes=[len(grouped[p]['alerts']) for p in comparable]
        if len(volumes)>=cfg['minimum_peers'] and median(volumes)>0 and len(alerts)<median(volumes)*cfg['low_activity_ratio']:
            emit('low_activity','Low activity relative to comparable entities','cyber_resilience',[cse],'cses',1,'Sector, cohort, criticality and declared size matched; subject excluded. Low volume requires context.',expectation={'expected':median(volumes),'observed':len(alerts),'gap':median(volumes)-len(alerts),'source':'Matched peer median'})
        if peers.get('available') and peers['median']>0 and closure[cid]>peers['median']*cfg['peer_deviation_multiplier']:
            emit('peer_deviation','Closure duration differs from peer baseline','security_operations',[a for a in alerts if a.closure_timestamp and a.severity in cfg['expected_escalation_severities']],'alerts',len(alerts),'High-severity median closure exceeds configured multiple of matched peer median.')
        if cfg['metric_integrity_enabled']:
            weak_ids={c.case_id for c in weak}
            emit('metric_integrity','Fast closure with weak supporting evidence','operational_discipline',[a for a in fast if a.case_id in weak_ids],'alerts',len(alerts),'Intersection of fast closure and limited submitted investigation events; no inference of intent.','high')
        entity['signal_count']=sum(s['cse_id']==cid for s in signals)
        entity['high_priority']=sum(s['cse_id']==cid and s['severity']=='high' for s in signals)
    return {'version':VERSION,'config':cfg,'configuration_hash':hashlib.sha256(canonical_json(cfg)).hexdigest(),'signals':signals,'entities':entities,'trends':trends,'unavailable':unavailable}
