import { fetchStatus } from "../../../lib/status";
import { backendBaseUrl } from "../../../lib/backend-url";

export const dynamic = "force-dynamic";
export async function GET() {
  const result = await fetchStatus(backendBaseUrl(process.env));
  return Response.json(result, { status: result.ok ? 200 : 503, headers: { "Cache-Control": "no-store" } });
}
