"""Draft selected evidence; no model download, persistence or cloud fallback."""
import argparse
import json
from pathlib import Path
from sat_sa.assistance.summary import draft_summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path('data/sample'))
    parser.add_argument('--dataset',default='demo')
    parser.add_argument('--cse',required=True)
    parser.add_argument('--table',default='alerts')
    parser.add_argument('--limit',type=int,default=3)
    parser.add_argument('--offset',type=int,default=0)
    parser.add_argument('--provider',choices=['ollama','mistral'],default='ollama')
    parser.add_argument('--allow-cloud',action='store_true',help='Consent to send selected evidence to Mistral')
    args=parser.parse_args()
    try:
        result=draft_summary(args.root,args.dataset,args.cse,args.table,args.limit,offset=args.offset,
                             provider=args.provider,cloud_consent=args.allow_cloud)
    except (ValueError,OSError) as exc:
        parser.exit(1,f'{exc}\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
