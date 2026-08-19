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
  await page.getByRole("button", { name: "项目与计划", exact: true }).click();
  await page.waitForTimeout(120);

  const shots = [
    ["V10.6-R3-01-projects-empty.png", "empty"],
    ["V10.6-R3-02-r2-project-enter.png", "normal"],
    ["V10.6-R3-14-no-permission.png", "no-permission"],
  ];
  for (const [name, state] of shots) {
    if (state === "normal") {
      await page.locator(`.state-switcher button[data-state="normal"]`).click();
    } else {
      await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    }
    await page.waitForTimeout(100);
    await page.screenshot({ path: path.join(outDir, name) });
    console.log(`saved ${name}`);
  }

  const states = ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"];
  for (const state of states) {
    await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    await page.waitForTimeout(80);
    const name = `V10.6-R3-mock-state-${state}.png`;
    await page.screenshot({ path: path.join(outDir, name) });
    console.log(`saved ${name}`);
  }

  const narrow = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await narrow.goto("file:///" + previewPath.replace(/\\/g, "/"), { waitUntil: "load" });
  await narrow.getByRole("button", { name: "项目与计划", exact: true }).click();
  await narrow.waitForTimeout(100);
  await narrow.screenshot({ path: path.join(outDir, "V10.6-R3-15-narrow-responsive.png") });
  await narrow.close();
  console.log("saved V10.6-R3-15-narrow-responsive.png");
} finally {
  await browser.close();
}
