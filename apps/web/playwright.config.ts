import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  use: { baseURL: process.env.SAT_SA_WEB_URL ?? "http://127.0.0.1:3000", channel: process.env.PLAYWRIGHT_CHANNEL ?? "msedge", headless: true },
  reporter: "list",
});
