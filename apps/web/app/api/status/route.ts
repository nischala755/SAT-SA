import { fetchStatus } from "../../../lib/status";

export const dynamic = "force-dynamic";
export async function GET() {
  const result = await fetchStatus(process.env.SAT_SA_API_URL ?? "http://127.0.0.1:8000");
  return Response.json(result, { status: result.ok ? 200 : 503, headers: { "Cache-Control": "no-store" } });
}
