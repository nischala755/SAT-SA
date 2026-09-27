"""Explicit expectations: absence of evidence is never proof of control failure."""
def monitoring_gaps(assets,alerts):
    seen={a.asset_id for a in alerts if a.asset_id}
    expected=[a for a in assets if a.monitoring_expected and a.criticality=='critical']
    return expected,[a for a in expected if a.asset_id not in seen]

def category_gaps(alerts,expected):
    observed={a.alert_category for a in alerts}
    return sorted(set(expected)-observed)
