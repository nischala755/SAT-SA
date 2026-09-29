"""Check that a Cloudflare HTTPS demo serves the app but gates evidence."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def request(url, token=None):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    try:
        with urlopen(Request(url, headers=headers), timeout=20) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='Cloudflare HTTPS origin, without trailing path')
    parser.add_argument('--env-file', type=Path, default=Path('.env.cloudflare.local'))
    parser.add_argument('--allow-local-http', action='store_true', help='Only for loopback preflight')
    args = parser.parse_args()
    parsed = urlparse(args.url)
    local_http = args.allow_local_http and parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost')
    if not (parsed.scheme == 'https' or local_http) or not parsed.hostname or parsed.path not in ('', '/'):
        raise SystemExit('Supply an HTTPS Cloudflare origin or --allow-local-http with loopback')
    entries = dict(line.split('=', 1) for line in args.env_file.read_text(encoding='utf-8').splitlines()
                   if line and not line.startswith('#') and '=' in line)
    identities = json.loads(entries['SAT_SA_AUTH_TOKENS'])
    token = next(iter(identities))
    base = args.url.rstrip('/')
    status, health = request(base + '/api/status')
    assert status == 200 and health['ok'] and health['health']['storage_ready'], (status, health)
    status, _ = request(base + '/api/service/datasets')
    assert status == 401, f'Unauthenticated evidence API returned {status}'
    status, identity = request(base + '/api/service/identity', token)
    assert status == 200 and identity['role'] == 'administrator', (status, identity)
    status, datasets = request(base + '/api/service/datasets', token)
    assert status == 200 and datasets['total'] >= 1, (status, datasets)
    print(json.dumps({'origin': base, 'backend_storage_ready': True,
                      'unauthenticated_evidence_blocked': True,
                      'authenticated_identity': identity['actor'],
                      'registered_datasets': datasets['total']}))


if __name__ == '__main__':
    main()
