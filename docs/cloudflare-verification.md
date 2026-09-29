# Cloudflare temporary deployment verification — 2026-09-29

**Status:** Temporary Quick Tunnel working. Stable named tunnel and Access policy unverified because no Cloudflare account/domain/token is available in this workspace. The tunnel depends on this Docker host and Internet access; it does not replace the verified offline deployment.

| Command | Exit | Observed result |
| --- | ---: | --- |
| `.venv\Scripts\python.exe scripts/prepare_cloudflare_demo.py` | 0 | Created Git-ignored `.env.cloudflare.local` with a new administrator bearer identity; secret was not printed. |
| `docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml config --quiet` | 0 | Authenticated API override validated. |
| `docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml config --quiet` with a temporary placeholder `CLOUDFLARE_TUNNEL_TOKEN` | 0 | Named-tunnel configuration validated; no real tunnel token or hostname provisioned. |
| `docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml up --build --wait -d` | 0 | Rebuilt API/web; both healthy. |
| `.venv\Scripts\python.exe scripts/verify_cloudflare_demo.py http://127.0.0.1:3001 --allow-local-http` | 0 | Local preflight: storage ready, unauthenticated evidence 401, authenticated identity and seven dataset versions. |
| `docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.quick.yaml up --wait -d` | 0 | Official `cloudflare/cloudflared:latest` image started a Quick Tunnel on the Compose network. Logs reported connector version 2026.9.3 and registered QUIC connection. |
| `.venv\Scripts\python.exe scripts/verify_cloudflare_demo.py https://lee-delivery-complement-francisco.trycloudflare.com` | 0 | Public HTTPS health and storage passed; unauthenticated evidence blocked; authenticated identity and datasets passed. |
| `node scripts/verify-cloudflare-browser.mjs https://lee-delivery-complement-francisco.trycloudflare.com` in `apps/web` | 0 | Public page rendered; backend connected; authenticated evidence visible in Edge. |
| `.venv\Scripts\python.exe -m pytest -q` | 0 | 109 tests passed, one upstream deprecation warning. |
| `npm test` in `apps/web`; `npm run typecheck` in `apps/web` | 0 each | Six frontend unit tests passed; TypeScript clean. |

The temporary URL is not an uptime guarantee or a stable submission address. No Cloudflare Access application, named tunnel, custom domain, Cloudflare-hosted API, or persistent Cloudflare storage has been provisioned. The API and DuckDB/Parquet volume remain on the local Docker host. The default Compose deployment is unchanged and remains the offline path.
