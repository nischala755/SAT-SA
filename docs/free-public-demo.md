# Free public SAT-SA demo from a Windows computer

This option runs the existing API, web app, and persistent DuckDB/Parquet volume in local Docker. A Tailscale Funnel publishes **synthetic demonstration data only** at a stable HTTPS `ts.net` address. It uses the free Tailscale Personal plan for a non-commercial demo. The public site is available only while the computer, Docker Desktop, and Internet connection are running. The normal offline Compose deployment remains separate.

## First setup

1. Create or sign in to a [Tailscale Personal account](https://tailscale.com/pricing). The Docker service prints a device-authorization URL; approve only the `sat-sa-demo` device.
2. Create the ignored `.env.cloudflare.local` bearer identity using `python scripts/prepare_cloudflare_demo.py` if it does not already exist. Keep its token private. Despite the filename, this configuration also secures the Tailscale demo; the API runs with `SAT_SA_DEMO_MODE=false`.
3. From the repository root, start the local app and Tailscale container:

   ```powershell
   docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.tailscale.yaml up -d api web tailscale
   docker logs --tail 30 sat-sa-tailscale-1
   ```

4. After device approval, enable Funnel. Tailscale may print another URL to authorize public Funnel access; complete that account step, then repeat the command.

   ```powershell
   docker exec sat-sa-tailscale-1 tailscale --socket=/tmp/tailscaled.sock funnel --bg http://web:3000
   docker exec sat-sa-tailscale-1 tailscale --socket=/tmp/tailscaled.sock funnel status
   ```

5. Open the reported `https://sat-sa-demo.<tailnet>.ts.net` URL. Check `/api/status` and the **Backend connected** UI state. Use the configured identity token to access the synthetic dataset. Do not submit restricted or real CSE evidence to this public demo.

The `sat-sa-data` Docker volume holds application data, and `sat-sa-tailscale-state` holds the tunnel identity and Funnel configuration across container restarts. The overlay sets the app and tunnel to restart unless stopped. Docker Desktop still must be running after a Windows reboot. Tailscale's free service has bandwidth limits and gives no always-on guarantee for your computer.

## Stop and resume

Stop public access without deleting persistent data:

```powershell
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.tailscale.yaml stop tailscale
```

Resume with:

```powershell
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.tailscale.yaml up -d api web tailscale
```

The stable URL resumes when the same authenticated Tailscale node returns online. Do not run `docker compose down -v`; that would delete the data and Tailscale identity volumes. The older Cloudflare Quick Tunnel has a random URL and is not needed once this route is verified.
