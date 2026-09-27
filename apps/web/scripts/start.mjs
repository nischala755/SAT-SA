import { cpSync, existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";

const base = path.resolve(".next/standalone/apps/web");
const server = path.join(base, "server.js");
if (!existsSync(server)) throw new Error("Production build missing. Run npm run build first.");
cpSync(".next/static", path.join(base, ".next/static"), { recursive: true });
const child = spawnSync(process.execPath, [server], {
  stdio: "inherit",
  env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1", HOSTNAME: "127.0.0.1", PORT: process.env.PORT ?? "3000" },
});
process.exit(child.status ?? 1);
