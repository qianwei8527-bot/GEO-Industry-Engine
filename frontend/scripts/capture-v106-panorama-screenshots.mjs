import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";

const base = process.env.V106_PANORAMA_BASE || "http://localhost:3109";
const registry = JSON.parse(readFileSync(path.resolve("..", "config", "panorama", "page-registry.json"), "utf8"));
const outDir = path.resolve("..", "docs", "generated_images");
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

const TEMPLATE_REPRESENTATIVES = {
  workbench: "owner-today",
  list: "ops-runtime",
  detail: "public-home",
  config: "ops-system",
  management: "gov-approvals",
  canvas: "owner-intel",
};
const STATES = ["normal", "loading", "empty", "partial", "blocked", "error", "no_permission"];
const NARROW_PAGES = [
  ["owner", "owner-today"],
  ["public", "public-home"],
  ["operations", "ops-overview"],
  ["governance", "gov-permissions"],
];

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

async function openPage(page, pageId) {
  await page.goto(`${base}/panorama?page=${pageId}`, { waitUntil: "domcontentloaded" });
  await page.getByText("dataMode=fixture", { exact: false }).first().waitFor({ timeout: 30000 });
  await page.waitForTimeout(250);
}

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto(`${base}/panorama`, { waitUntil: "domcontentloaded" });
  await page.getByText("恒域世界全景", { exact: false }).first().waitFor({ timeout: 30000 });
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(outDir, "V10.6-PANORAMA-01-overview.png") });

  for (const entry of registry.pages) {
    await openPage(page, entry.page_id);
    await page.screenshot({ path: path.join(outDir, `V10.6-PANORAMA-PAGE-${entry.page_id}.png`) });
  }

  for (const [template, pageId] of Object.entries(TEMPLATE_REPRESENTATIVES)) {
    for (const state of STATES) {
      await openPage(page, pageId);
      const button = page.getByRole("button", { name: state, exact: true }).first();
      await button.waitFor({ state: "visible", timeout: 20000 });
      await button.click();
      await page.waitForTimeout(200);
      await page.screenshot({ path: path.join(outDir, `V10.6-PANORAMA-STATE-${template}-${state}.png`) });
    }
  }
  if (errors.length > 0) throw new Error(`panorama page errors: ${errors.join(" | ")}`);
  await context.close();

  for (const [surface, pageId] of NARROW_PAGES) {
    const narrow = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const narrowPage = await narrow.newPage();
    await openPage(narrowPage, pageId);
    const overflow = await narrowPage.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    if (overflow.scrollWidth > overflow.clientWidth + 1) {
      throw new Error(`${surface} narrow overflow: ${overflow.scrollWidth} > ${overflow.clientWidth}`);
    }
    await narrowPage.screenshot({
      path: path.join(outDir, `V10.6-PANORAMA-NARROW-${surface}.png`),
      fullPage: true,
    });
    await narrow.close();
  }

  console.log(
    `PASS panorama pages=${registry.pages.length} states=${Object.keys(TEMPLATE_REPRESENTATIVES).length * STATES.length} narrow=4 errors=0`,
  );
} finally {
  await browser.close();
}
