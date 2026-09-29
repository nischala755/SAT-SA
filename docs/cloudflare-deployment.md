# Cloudflare deployment for the synthetic SAT-SA demo

SAT-SA's FastAPI process needs a persistent, writable DuckDB/Parquet filesystem. The working Cloudflare path is a **Tunnel in front of the existing Docker Compose web service**. The API and data remain on the host running Docker; only the web hostname is exposed through Cloudflare. This is a cloud demonstration exception. The default `docker compose up --build --wait` path remains local and offline.

Cloudflare Containers do not currently provide persistent local disks: a sleeping instance restarts with a fresh disk. Mounting R2 through FUSE is possible but is not equivalent to a local DuckDB filesystem and would require a measured storage redesign. A frontend-only Workers deployment would also leave the Python API unhosted. See Cloudflare's [Containers FAQ](https://developers.cloudflare.com/containers/faq/) and [Tunnel guide](https://developers.cloudflare.com/tunnel/get-started/).

## What is running now

On 2026-09-29, the temporary Cloudflare Quick Tunnel was verified at `https://lee-delivery-complement-francisco.trycloudflare.com`. It is **not a durable hostname**: the URL can change when the connector restarts, and the Docker host must stay on and connected. Cloudflare describes Quick Tunnels as testing-only. This route has application bearer authentication but no Cloudflare Access policy, so use it only with the synthetic demo. The current local token lives in ignored `.env.cloudflare.local`; it is not committed or printed in deployment logs.

The public smoke check showed `/api/status` healthy, `/api/service/datasets` returning 401 without a token, and an authenticated identity and datasets response. A real browser loaded the public Next.js page, connected to the backend and displayed evidence after token entry. See [verification](cloudflare-verification.md).

## Reproduce the temporary test tunnel

From the repository root on a Docker host, run:

```powershell
.venv\Scripts\python.exe scripts/prepare_cloudflare_demo.py
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.quick.yaml up --build --wait -d
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.quick.yaml logs --tail 40 tunnel
```

The first command creates `.env.cloudflare.local` once and refuses to overwrite it; on Linux it creates the file with owner-only `0600` permissions. If you are using a fresh clone without `.venv`, use any Python 3.12+ interpreter for that script. Copy the generated `https://...trycloudflare.com` URL from the tunnel logs. Open `.env.cloudflare.local` **locally** and copy the JSON object's key into the application's **Bearer token** field; do not paste the key into chat or commit the file. The API is in configured-identity mode, so evidence APIs fail closed without that token.

Verify the temporary route:

```powershell
.venv\Scripts\python.exe scripts/verify_cloudflare_demo.py https://YOUR-QUICK-URL.trycloudflare.com
cd apps/web
node scripts/verify-cloudflare-browser.mjs https://YOUR-QUICK-URL.trycloudflare.com
```

`verify_cloudflare_demo.py` checks HTTPS health, unauthenticated denial, authenticated identity and dataset access. The browser check verifies the actual public page and evidence view. Keep the Docker host and `tunnel` container running while showing judges the URL. To stop public exposure without deleting data, run `docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.quick.yaml stop tunnel`.

**Stop the tunnel before switching back to the unauthenticated default Compose configuration.** Docker Compose can leave the tunnel container running as an orphan if you omit its override file; leaving it up while restoring local demo identity would expose the synthetic evidence without the cloud-mode bearer gate. After stopping it, restore local mode with `docker compose up --wait -d --remove-orphans`.

## Make the URL stable under your Cloudflare account

This step requires an active domain in your Cloudflare account. The workspace has no Cloudflare account login, active domain, named tunnel or tunnel token, so it has **not** been completed or claimed as verified.

1. In Cloudflare Zero Trust, create a **self-hosted Access application** for the intended hostname (for example, `vista.example.com`) and allow only the judge/team email identities that should view the demo. Do this **before** adding a public tunnel route. Cloudflare warns that a published application without an Access application is public. Turn on **Protect with Access** for the tunnel route where offered. [Cloudflare Access instructions](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/).
2. In **Networking → Tunnels**, create a remotely managed tunnel. Add a **Published application** route from the exact hostname to `http://web:3000`. This URL is resolved inside the Compose network; do not route the API port or its DuckDB volume publicly. [Tunnel setup](https://developers.cloudflare.com/tunnel/get-started/).
3. Copy the remotely managed tunnel token into `.env.cloudflare.local` as a new `CLOUDFLARE_TUNNEL_TOKEN=...` line. Keep it out of Git, screenshots, logs and chat. A tunnel token grants the ability to run a connector for that tunnel. [Tunnel token guidance](https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/).
4. Start the named connector, replacing the temporary Quick Tunnel service:

   ```powershell
   docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml up --wait -d --remove-orphans
   docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml ps
   ```

5. From a separate browser session, verify that an unapproved visitor is blocked by Access, an approved visitor reaches the SAT-SA page, and the application's bearer token is still required for evidence. Complete an actual signal → source → review → audit walkthrough. Restart the API and connector, then verify the dataset hash, review and audit persist. Record the stable URL and results before announcing the named deployment complete.

Cloudflare Access is an additional gate, not a substitute for SAT-SA's application identity. This cloud route is for **synthetic evidence only**; it is not an NCIIPC-controlled, offline production deployment. For real restricted submissions, use the approved local deployment and organizational network controls.

## Keep the named deployment online

A named hostname is stable, but a tunnel on a laptop still disappears when that laptop sleeps. For an always-available hackathon demo, use an always-on Linux VPS or organizational server with persistent SSD storage and Docker Engine plus the Compose plugin. A planning size for the **small synthetic demo** is 2 vCPU, 4 GiB RAM and 20 GiB SSD; this is not a tested large-data minimum. Keep DNS in your Cloudflare account and use the named tunnel above. Cloudflare does not store the DuckDB data for this design.

On the server, clone the published repository, create a **new** local demo credential, and place your named-tunnel token in that ignored file. The token must come from your own Cloudflare account after the Access application and tunnel route are configured. Do not copy the temporary local `.env.cloudflare.local` from a laptop.

```bash
git clone https://github.com/nischala755/ViSTa.git
cd ViSTa
python3 scripts/prepare_cloudflare_demo.py
# Edit .env.cloudflare.local locally on the VPS and add:
# CLOUDFLARE_TUNNEL_TOKEN=<your token from Cloudflare>
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml -f compose.cloudflare.prod.yaml up --build --wait -d
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml -f compose.cloudflare.prod.yaml ps
```

The production override restarts all three containers after a Docker daemon/server restart and bounds log growth. The tunnel connector image is pinned to a reviewed digest rather than a moving `latest` tag. The base Compose file binds both HTTP ports only to `127.0.0.1`; Cloudflare routes external traffic to `http://web:3000` on the private Compose network. Keep one API instance because DuckDB metadata has one writer. Enable the Docker service at boot and use your server provider's monitoring/restart alerts. Avoid deploying restricted CSE records to this demo server.

After the first deploy, open the stable HTTPS hostname in a private browser. Confirm Cloudflare Access blocks a visitor outside the allow policy and lets an approved visitor through; then enter the application's local bearer token and run analytics on `demo` if no run exists. Verify overview → signal → source record → review → audit, plus `/api/status`. Restart the server and repeat the check. Until the URL and restart behavior are observed, the permanent deployment remains unverified.

Back up the Docker volume while the API is stopped, then move the backup **off the VPS**. The volume name under the repository's default Compose project is `sat-sa_sat-sa-data`. One manual snapshot example is:

```bash
mkdir -p backups
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml -f compose.cloudflare.prod.yaml stop api
docker run --rm -v sat-sa_sat-sa-data:/source:ro -v "$PWD/backups:/backup" alpine:3.20 sh -c 'tar -czf /backup/sat-sa-$(date +%Y%m%dT%H%M%S).tgz -C /source .'
docker compose --env-file .env.cloudflare.local -f compose.yaml -f compose.cloudflare.yaml -f compose.cloudflare.tunnel.yaml -f compose.cloudflare.prod.yaml start api
```

This is a maintenance example, not a tested backup/restore procedure; validate a restore into a separate volume before relying on it. Keep the tunnel token and SAT-SA bearer credentials out of backup locations accessible to viewers. A VPS incurs ongoing hosting charges and needs operating-system patching, disk monitoring and credential rotation.
