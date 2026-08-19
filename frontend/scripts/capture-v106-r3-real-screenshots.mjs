import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";

const base = process.env.V106_REAL_BASE || "http://localhost:3109";
const realm = process.env.V106_R3_REAL_REALM;
const token = process.env.V106_R3_REAL_TOKEN;
const outsiderToken = process.env.V106_R3_REAL_OUTSIDER_TOKEN;
if (!realm || !token || !outsiderToken) {
  throw new Error("set V106_R3_REAL_REALM, V106_R3_REAL_TOKEN and V106_R3_REAL_OUTSIDER_TOKEN");
}
const outDir = path.resolve("..", "docs", "generated_images");
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await context.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: token });
  const page = await context.newPage();
  const errors = [];
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`${base}/realm/${realm}/projects`, { waitUntil: "domcontentloaded" });
  await page.getByText("项目与执行计划", { exact: false }).first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(1500);
  const bodyText = await page.locator("body").innerText();
  if (bodyText.includes("realm_template") || bodyText.includes("realm-template-geo-starter")) {
    throw new Error("real page still contains realm_template wording");
  }
  await page.screenshot({ path: path.join(outDir, "V10.6-R3-REAL-01-projects-page.png"), fullPage: true });
  await page.evaluate(() => {
    const heading = Array.from(document.querySelectorAll("h2, div")).find((element) =>
      element.textContent?.includes("正式任务与日程"),
    );
    heading?.scrollIntoView({ block: "start" });
  });
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(outDir, "V10.6-R3-REAL-02-tasks-progress-overdue.png") });
  console.log(`real owner errors=${errors.length}`);
  if (errors.length) console.log(errors.join("\n"));
  await context.close();

  const narrow = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await narrow.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: token });
  const narrowPage = await narrow.newPage();
  await narrowPage.goto(`${base}/realm/${realm}/projects`, { waitUntil: "domcontentloaded" });
  await narrowPage.getByText("项目与执行计划", { exact: false }).first().waitFor({ timeout: 20000 });
  await narrowPage.waitForTimeout(1000);
  const overflow = await narrowPage.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  if (overflow.scrollWidth > overflow.clientWidth + 1) {
    throw new Error(`narrow overflow: ${overflow.scrollWidth} > ${overflow.clientWidth}`);
  }
  await narrowPage.screenshot({ path: path.join(outDir, "V10.6-R3-REAL-03-narrow-responsive.png"), fullPage: true });
  await narrow.close();

  const denied = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await denied.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: outsiderToken });
  const deniedPage = await denied.newPage();
  await deniedPage.goto(`${base}/realm/${realm}/projects`, { waitUntil: "domcontentloaded" });
  await deniedPage.getByText("无权限", { exact: false }).first().waitFor({ timeout: 20000 });
  await deniedPage.waitForTimeout(800);
  await deniedPage.screenshot({ path: path.join(outDir, "V10.6-R3-REAL-04-no-permission.png") });
  await denied.close();
  console.log("saved real screenshots");
} finally {
  await browser.close();
}
