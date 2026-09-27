import { expect, test } from "@playwright/test";

test("shell connects to backend and requests only local resources", async ({ page }, testInfo) => {
  const remote: string[] = [];
  page.on("request", request => {
    if (new URL(request.url()).origin !== new URL(testInfo.project.use.baseURL as string).origin) remote.push(request.url());
  });
  await page.route("**/*", route => new URL(route.request().url()).origin === new URL(testInfo.project.use.baseURL as string).origin ? route.continue() : route.abort("internetdisconnected"));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "SAT-SA", exact: true })).toBeVisible();
  await expect(page.getByText("Backend connected", { exact: true })).toBeVisible();
  await expect(page.getByText("Local metadata storage ready", { exact: true })).toBeVisible();
  const response = await page.request.get("/api/status");
  expect(response.status()).toBe(200);
  expect((await response.json()).health.registered_datasets).toBe(1);
  await page.screenshot({ path: "../../artifacts/shell.png", fullPage: true });
  expect(remote).toEqual([]);
});

test("backend failure is visible and retry recovers", async ({ page }) => {
  await page.route("**/api/status", route => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ ok: false, message: "Backend unavailable. Check the local API service and retry." }) }));
  await page.goto("/");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Backend unavailable");
  await expect(page.getByText("Backend connected", { exact: true })).toHaveCount(0);
  await page.unroute("**/api/status");
  await page.getByRole("button", { name: "Retry connection" }).click();
  await expect(page.getByText("Backend connected", { exact: true })).toBeVisible();
});
