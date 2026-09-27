import { chromium } from "../apps/web/node_modules/@playwright/test/index.mjs";
import assert from "node:assert/strict";
const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL ?? "msedge", headless: true });
try {
  const page = await browser.newPage();
  await page.goto(process.argv[2]);
  const alert = page.getByRole("main").getByRole("alert");
  await alert.waitFor();
  assert.match(await alert.innerText(), /Backend unavailable/);
  assert.equal(await page.getByText("Backend connected", { exact: true }).count(), 0);
  await page.screenshot({ path: "artifacts/real-backend-outage.png", fullPage: true });
  console.log("Real backend outage is visibly reported in the browser");
} finally { await browser.close(); }
