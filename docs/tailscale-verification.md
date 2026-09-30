# Free Tailscale Funnel deployment verification — 2026-09-30

The synthetic SAT-SA demo is publicly reachable at **https://sat-sa-demo.tail2e8b39.ts.net/** while this Windows host, Docker Desktop and its Internet connection are running. The core offline Compose path remains separate. This is a user-authorized public demo, not a deployment for restricted NCIIPC evidence.

| Check | Observed result |
| --- | --- |
| Compose overlay | `docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.tailscale.yaml config -q` exited 0. |
| Tailscale identity | `tailscale status` showed `sat-sa-demo` connected at `100.74.180.27`; the container had zero login-loop restarts after replacing `containerboot` with a persistent `tailscaled` daemon. |
| Funnel | `tailscale funnel --bg http://web:3000` completed after account approval; `tailscale funnel status` reported the HTTPS address proxying `http://web:3000`. |
| Public API/storage | `.venv\Scripts\python.exe scripts/verify_cloudflare_demo.py https://sat-sa-demo.tail2e8b39.ts.net` exited 0: backend storage ready, unauthenticated evidence blocked, authenticated identity accepted, seven registered datasets. The verification script is provider-neutral despite its historical name. |
| Public browser | `node scripts/verify-cloudflare-browser.mjs https://sat-sa-demo.tail2e8b39.ts.net` from `apps/web` exited 0: frontend loaded, backend connected, authenticated evidence visible. |
| Restart persistence | `docker restart sat-sa-tailscale-1` completed. After the daemon reconnected, the same device identity, Funnel URL and proxy configuration returned. The public API/storage check passed again at the same URL. |

The Tailscale identity resides in `sat-sa-tailscale-state`; application evidence resides in `sat-sa-data`. Do not run `docker compose down -v`. A Windows reboot still requires Docker Desktop to start. The host may sleep, lose connectivity, or be powered off, so this is an on-demand public demo rather than continuously hosted infrastructure. Tailscale's free Personal plan and Funnel relay limits also apply. The local offline product does not call Tailscale or any external AI service.
