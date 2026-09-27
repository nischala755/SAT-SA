"""Robust descriptive peer statistics; caller excludes subject and matches cohort."""
from statistics import median, quantiles

def peer_stats(value, peers, minimum=3):
    if len(peers)<minimum:
        return {'available':False,'count':len(peers),'reason':'Insufficient comparable peers'}
    center=median(peers); quartiles=quantiles(peers,n=4,method='inclusive')
    return {'available':True,'count':len(peers),'median':center,'percentile':100*sum(p<=value for p in peers)/len(peers),
            'iqr':quartiles[2]-quartiles[0],'mad':median(abs(p-center) for p in peers),'deviation':value-center}
