import Ajv from "ajv";
import healthSchema from "../../../data/schemas/HealthStatus.json";
import type { HealthStatus } from "../../../packages/shared-types/src/generated";

const validateHealth = new Ajv({ strict: true }).compile<HealthStatus>(healthSchema);
export type StatusResult = { ok: true; health: HealthStatus } | { ok: false; message: string };
const unavailable: StatusResult = { ok: false, message: "Backend unavailable. Check the local API service and retry." };

export async function fetchStatus(baseUrl: string, timeoutMs = 3000): Promise<StatusResult> {
  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/api/v1/health`, {
      cache: "no-store", signal: AbortSignal.timeout(timeoutMs), redirect: "error",
    });
    if (!response.ok) return unavailable;
    const health: unknown = await response.json();
    if (!validateHealth(health) || health.status !== "ok" || !health.storage_ready || health.registered_datasets === null) {
      return { ok: false, message: "Backend unavailable or returned an invalid storage status. Check local service logs." };
    }
    return { ok: true, health };
  } catch {
    return unavailable;
  }
}
