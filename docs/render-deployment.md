# Render deployment of the synthetic SAT-SA prototype

This guide prepares the existing two-service architecture for Render. **A live Render deployment has not yet been created or verified.** The repository's `render.yaml` passes the published Render JSON Schema locally; Render's account-aware Blueprint validation returned HTTP 401 because no Render account is authenticated in this workspace. The local Docker build and private-host proxy smoke test passed. Do not treat this document as a live deployment certificate.

## Why Render

SAT-SA currently stores immutable Parquet evidence and DuckDB metadata on one local filesystem, with a single API writer. Render offers a paid persistent disk on a single-instance service and private networking between that API and a public Next.js frontend. Cloudflare Workers' filesystem is ephemeral, so moving the API and DuckDB/Parquet storage wholly to Workers would be an architectural migration, not a deployment configuration. The default local/offline application remains available; deploying to Render is the user-requested cloud exception.

The Blueprint creates:

| Service | Exposure | Compute | Persistent state |
| --- | --- | --- | --- |
| `sat-sa-api` | Render private network only | `1c-2g`, one instance | 1 GB disk mounted at `/var/lib/sat-sa` |
| `sat-sa-web` | Public HTTPS web service | `0.5c-512mb`, one instance | None; all state comes from private API |

Both use the existing repository Dockerfiles and the Singapore region. The web service receives the API's private `hostport` through a Render service reference; its server-side proxy adds `http://`. No backend public URL or browser-to-backend cross-origin access is required. `SAT_SA_DEMO_MODE=false` makes bearer authentication mandatory, even though the initial evidence is synthetic. The API startup command still generates/registers that synthetic demo before the API opens. Because non-demo mode does not queue an automatic analytics run, the provisioned administrator/examiner selects `demo` and runs analytics after signing in.

Render currently lists the selected compute sizes at **$25/month** (API) and **$7/month** (web), plus **$0.25/GB/month** for the persistent disk, subject to current pricing, usage, taxes and account terms. The Blueprint is a paid deployment. A Render free service cannot have the persistent disk that this architecture needs, and free web services cannot receive private-network traffic. Check [current compute pricing](https://render.com/pricing), [persistent-disk rules](https://render.com/docs/disks), and [private-network rules](https://render.com/docs/private-network) before provisioning.

## Create the services

1. Sign in to Render and connect the GitHub repository `https://github.com/nischala755/VISTA` to the intended workspace. Select **New → Blueprint** and use the repository's root `render.yaml` on branch `main`. Inspect the two services, region, plans and disk before syncing.
2. During Blueprint creation, set the prompted `SAT_SA_AUTH_TOKENS` secret on **`sat-sa-api`**. It must be a JSON map from a newly generated, high-entropy bearer token to a server-owned actor and role. Example shape (the example token is deliberately unusable):

   ```json
   {"REPLACE_WITH_A_NEW_RANDOM_TOKEN":{"actor":"prototype-owner","role":"administrator"}}
   ```

   Store the real token in a password manager. Do not commit it, paste it into issues/chat, or reuse the optional Mistral key. The web service needs no shared secret; an authorized examiner enters the bearer token into the visible **Configured identity token** field. The value stays in page memory and is sent to the same-origin proxy as an Authorization header.
3. Confirm the API's disk is mounted at `/var/lib/sat-sa` and the service has **one instance**. Do not remove the disk or scale the DuckDB writer horizontally. Confirm both services share the Singapore region and that `sat-sa-web` has `SAT_SA_API_HOSTPORT` linked from the private API.
4. Let the API deploy and initialize storage. The web service's `/api/status` health check will report unavailable until it can reach healthy API storage. On the public web URL, check **Backend connected**, enter the token, choose `demo`, then select **Run analytics**. Inspect an entity, source evidence, and a human review. No finding is generated automatically.

## Post-deployment verification

Use the actual web URL shown in Render; do not guess the generated subdomain. From a terminal with access to it:

```powershell
$web = 'https://YOUR-WEB-SERVICE.onrender.com'
$status = Invoke-RestMethod "$web/api/status"
$status.ok
$status.health.storage_ready
$status.health.registered_datasets
```

Expect `true`, `true`, and at least `1`. The backend has no public URL. In the browser, enter the token, run analytics on `demo`, open a CSE signal and source record, record a synthetic human outcome, then check Audit trail. Restart/redeploy the API and verify the same dataset hash, run, review and audit remain. Also verify the frontend shows an error if the API is unavailable. Record the resulting public URL, run ID and exact status in a deployment verification report before claiming the cloud rollout succeeded.

The local checks performed while preparing this path were: 101 Python regressions, six frontend unit tests, six browser tests, TypeScript typecheck, a production web Docker build, local Render JSON Schema validation, and a temporary web container using `SAT_SA_API_HOSTPORT=api:8000` to reach the existing Compose API through both `/api/status` and `/api/service/datasets`. A non-demo API container with a temporary Docker volume started with a configured test token, rejected an unauthenticated identity request with 401, accepted the token, and retained the demo dataset/hash across restart. Render CLI v2.28.0's account-aware `blueprints validate render.yaml` returned 401. These checks establish local deployability of the configuration path, **not** successful provisioning, Render disk mounts or cloud persistence.

## Operating boundaries

- Use this deployment for **synthetic demonstration data only**. The prototype lacks SSO/MFA, fine-grained tenant isolation, signed audit, independent backups, rate limiting and accreditation for restricted SOC submissions. A configured bearer identity is a minimum exposure boundary, not production hardening.
- Render disk contents persist across service restarts/deploys, but the disk is available to one instance only and prevents zero-downtime deployment. Arrange application-consistent backups with the API stopped; a platform disk snapshot alone is not a validated DuckDB restore strategy.
- The cloud runtime requires Render's platform and network. The existing local deployment is the separately verified offline mode. Normal Render service networking does not prove denied outbound Internet access. Neither Qwen nor Mistral is deployed by this Blueprint.
- `SAT_SA_AUTH_TOKENS` is marked `sync: false`, so Render prompts on initial Blueprint creation. On later syncs or an additional preview environment, verify that the secret is still set; absent auth configuration makes the API fail closed.
- After a code push, inspect both deployments and rerun the post-deployment checks. Keep `sat-sa-api` at one instance while DuckDB owns metadata writes. Larger data and production identity/audit requirements need the architecture migration described in [completion verification](completion-verification.md).
