/** Resolve the backend only on the Next.js server. Render supplies its private host:port. */
export function backendBaseUrl(env: Record<string, string | undefined>): string {
  if (env.SAT_SA_API_URL) return env.SAT_SA_API_URL;
  if (env.SAT_SA_API_HOSTPORT) return `http://${env.SAT_SA_API_HOSTPORT}`;
  return "http://127.0.0.1:8000";
}
