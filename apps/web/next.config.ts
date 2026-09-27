import type { NextConfig } from "next";
import path from "node:path";

const root = path.resolve(process.cwd(), "../..");
const config: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: root,
  turbopack: { root },
  poweredByHeader: false,
};
export default config;
