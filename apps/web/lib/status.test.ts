import { createServer, type Server } from "node:http";
import { afterEach, describe, expect, it } from "vitest";
import { backendBaseUrl } from "./backend-url";

let server: Server | undefined;
afterEach(() => { server?.closeAllConnections(); server?.close(); });
async function endpoint(code: number, body: unknown, stall = false) {
  server = createServer((_req, res) => {
    if (stall) return;
    res.writeHead(code, { "content-type": "application/json" });
    res.end(JSON.stringify(body));
  });
  await new Promise<void>(resolve => server!.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("Missing test server port");
  return `http://127.0.0.1:${address.port}`;
}
async function implementation() {
  const path = "./status";
  try { return await import(path); }
  catch { throw new Error("Status client has not been implemented"); }
}
const healthy = { status: "ok", service: "sat-sa-api", software_version: "0.1.0", demo_mode: true, storage_ready: true, registered_datasets: 1, message: "Local metadata storage ready" };

describe("backend health boundary", () => {
  it("resolves a private service host and port without changing local defaults", () => {
    expect(backendBaseUrl({})).toBe("http://127.0.0.1:8000");
    expect(backendBaseUrl({ SAT_SA_API_HOSTPORT: "sat-sa-api.internal:8000" })).toBe("http://sat-sa-api.internal:8000");
    expect(backendBaseUrl({ SAT_SA_API_URL: "http://api:8000", SAT_SA_API_HOSTPORT: "ignored:8000" })).toBe("http://api:8000");
  });
  it("reads actual healthy status", async () => {
    const { fetchStatus } = await implementation();
    expect(await fetchStatus(await endpoint(200, healthy))).toEqual({ ok: true, health: healthy });
  });
  it("shows an unavailable state for HTTP failures", async () => {
    const { fetchStatus } = await implementation();
    const result = await fetchStatus(await endpoint(503, { ...healthy, status: "unavailable", storage_ready: false }));
    expect(result.ok).toBe(false);
    expect(result.message).toContain("unavailable");
  });
  it("rejects malformed health data instead of displaying success", async () => {
    const { fetchStatus } = await implementation();
    expect((await fetchStatus(await endpoint(200, { status: "ok" }))).ok).toBe(false);
  });
  it("times out a stalled backend", async () => {
    const { fetchStatus } = await implementation();
    const result = await fetchStatus(await endpoint(200, healthy, true), 40);
    expect(result.ok).toBe(false);
    expect(result.message).toContain("unavailable");
  });
  it("handles refused backend connections", async () => {
    const { fetchStatus } = await implementation();
    const url = await endpoint(200, healthy);
    await new Promise<void>(resolve => server!.close(() => resolve()));
    expect((await fetchStatus(url)).ok).toBe(false);
  });
});
