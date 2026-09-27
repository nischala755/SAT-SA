from datetime import datetime,timedelta,timezone
from sat_sa.signals import rules
from sat_sa.signals.engine import configuration
from sat_sa.negative_space.expectations import monitoring_gaps,category_gaps
from sat_sa_contracts.models import Alert,Case,Asset

P={'source_file':'fixture.json','source_record':'1','ingestion_batch':'test','transformation_version':'1'}
T=datetime(2025,1,1,tzinfo=timezone.utc)
def alert(i=0,**kw):
    return Alert(cse_id='C',alert_id=f'A{i}',timestamp=T+timedelta(days=i),severity='critical',source='test',alert_category='network',rule_use_case='test',asset_id='asset',provenance=P,**kw)
def case(i=0,**kw):
    return Case(cse_id='C',case_id=f'C{i}',opened_at=T,severity='critical',provenance=P,**kw)

def test_fast_closure_normal_and_missing():
    cfg=configuration()
    assert rules.fast_closure([alert(closure_timestamp=T+timedelta(minutes=2))],cfg)
    assert not rules.fast_closure([alert(closure_timestamp=T+timedelta(hours=2)),alert(1)],cfg)

def test_escalation_absence_and_present():
    cfg=configuration()
    assert rules.missing_escalation([alert(closure_timestamp=T+timedelta(hours=1))],[],cfg)
    assert not rules.missing_escalation([alert(closure_timestamp=T+timedelta(hours=1),escalation_timestamp=T+timedelta(minutes=10))],[],cfg)

def test_recurrence_window_boundary():
    cfg=configuration()
    assert len(rules.recurrence([alert(i) for i in range(4)],cfg))==4
    assert not rules.recurrence([alert(i*31) for i in range(4)],cfg)

def test_bursts_and_normal():
    cfg=configuration()
    assert len(rules.closure_bursts([case(i,closed_at=T+timedelta(hours=1)) for i in range(5)],cfg))==5
    assert not rules.closure_bursts([case(i,closed_at=T+timedelta(hours=i+1)) for i in range(5)],cfg)

def test_template_repetition_requires_weak_evidence():
    cfg=configuration()
    assert len(rules.repeated_templates([case(i,closed_at=T+timedelta(hours=1),closure_reason='same',investigation_steps_count=1) for i in range(10)],cfg))==10
    assert not rules.repeated_templates([case(i,closure_reason='same',investigation_steps_count=5) for i in range(10)],cfg)

def test_monitoring_expectation_and_category_presence():
    asset=Asset(cse_id='C',asset_id='asset',criticality='critical',environment='prod',system_type='server',monitoring_expected=True,provenance=P)
    assert monitoring_gaps([asset],[])[1]==[asset]
    assert monitoring_gaps([asset],[alert()])[1]==[]
    assert category_gaps([alert()],['network'])==[]

def test_weak_investigation_normal_and_absent():
    from sat_sa_contracts.models import InvestigationEvent
    cfg=configuration(); c=case(closed_at=T+timedelta(hours=1))
    assert rules.weak_investigation([c],[],cfg)==[c]
    events=[InvestigationEvent(cse_id='C',event_id=f'E{i}',case_id='C0',timestamp=T,event_type='review',actor_team='team',action='check',provenance=P) for i in range(2)]
    assert rules.weak_investigation([c],events,cfg)==[]
