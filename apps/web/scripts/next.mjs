import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const child = spawnSync(process.execPath, [require.resolve("next/dist/bin/next"), ...process.argv.slice(2)], {
  stdio: "inherit", env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
});
process.exit(child.status ?? 1);
