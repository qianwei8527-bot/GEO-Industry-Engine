import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";

const previewPath = path.resolve("..", "docs", "v106-all-pages-design-preview.html");
const outDir = path.resolve("..", "docs", "generated_images");
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto("file:///" + previewPath.replace(/\\/g, "/"), { waitUntil: "load" });
  await page.getByRole("button", { name: "执行与问题", exact: true }).click();
  await page.waitForTimeout(120);
  await page.locator(`.state-switcher button[data-state="normal"]`).click();
  await page.waitForTimeout(80);
  await page.screenshot({ path: path.join(outDir, "V10.6-R4-01-issue-workbench.png") });
  const states = ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"];
  for (const state of states) {
    await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    await page.waitForTimeout(80);
    await page.screenshot({ path: path.join(outDir, `V10.6-R4-mock-state-${state}.png`) });
    console.log(`saved V10.6-R4-mock-state-${state}.png`);
  }
  const narrow = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await narrow.goto("file:///" + previewPath.replace(/\\/g, "/"), { waitUntil: "load" });
  await narrow.getByRole("button", { name: "执行与问题", exact: true }).click();
  await narrow.waitForTimeout(80);
  await narrow.screenshot({ path: path.join(outDir, "V10.6-R4-02-narrow-responsive.png") });
  await narrow.close();
  console.log("saved V10.6-R4-02-narrow-responsive.png");
} finally {
  await browser.close();
}
