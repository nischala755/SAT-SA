"""Create an ignored, local bearer identity for a synthetic Cloudflare demo."""
import json
import secrets
from pathlib import Path


def main():
    destination = Path('.env.cloudflare.local')
    token = secrets.token_urlsafe(36)
    value = json.dumps({token: {'actor': 'cloudflare-demo-owner', 'role': 'administrator'}}, separators=(',', ':'))
    with destination.open('x', encoding='utf-8') as file:
        file.write('SAT_SA_AUTH_TOKENS=' + value + '\n')
        file.write('# Add CLOUDFLARE_TUNNEL_TOKEN=... for a named tunnel after configuring Cloudflare Access.\n')
    print(f'Created {destination.resolve()}; this file is ignored by Git. Do not share its contents.')


if __name__ == '__main__':
    main()
