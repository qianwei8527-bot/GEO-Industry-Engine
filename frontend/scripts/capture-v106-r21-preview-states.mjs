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
  await page.getByRole("button", { name: "客户与定位", exact: true }).click();
  await page.waitForTimeout(100);

  const states = ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"];
  for (const state of states) {
    await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    await page.waitForTimeout(120);
    const name = `V10.6-R2.1-mock-state-${state}.png`;
    await page.screenshot({ path: path.join(outDir, name) });
    console.log(`saved ${name}`);
    if (state === "partial") {
      const alt = "V10.6-R2-04-mock-state-partial.png";
      await page.screenshot({ path: path.join(outDir, alt) });
      console.log(`saved ${alt}`);
    }
  }
} finally {
  await browser.close();
}
