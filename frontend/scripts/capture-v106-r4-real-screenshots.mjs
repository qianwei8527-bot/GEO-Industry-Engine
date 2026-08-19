import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";

const base = process.env.V106_R4_REAL_BASE || "http://localhost:3109";
const realm = process.env.V106_R4_REAL_REALM;
const token = process.env.V106_R4_REAL_TOKEN;
const outsiderToken = process.env.V106_R4_REAL_OUTSIDER_TOKEN;
const issueTitle = process.env.V106_R4_REAL_ISSUE_TITLE || "发布渠道权限不足";
const openIssueTitle = process.env.V106_R4_REAL_OPEN_ISSUE_TITLE || "客户资料缺少联系方式";
if (!realm || !token || !outsiderToken || !issueTitle || !openIssueTitle) {
  throw new Error("set V106_R4_REAL_REALM, V106_R4_REAL_TOKEN, V106_R4_REAL_OUTSIDER_TOKEN, V106_R4_REAL_ISSUE_TITLE and V106_R4_REAL_OPEN_ISSUE_TITLE");
}
const outDir = path.resolve("..", "docs", "generated_images");
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

try {
  const errors = [];
  async function assertVisible(locator, label) {
    await locator.waitFor({ state: "visible", timeout: 20000 });
    if (!(await locator.isVisible())) {
      throw new Error(`${label} is not visible`);
    }
  }

  async function selectIssue(page, title) {
    const row = page.locator("button").filter({ hasText: title }).first();
    await assertVisible(row, `issue row ${title}`);
    await row.click();
    const detail = page.locator("div.rounded-md.border.border-slate-200.bg-white.p-3").filter({ hasText: title }).first();
    await assertVisible(detail, `issue detail ${title}`);
    return detail;
  }

  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await context.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: token });
  const page = await context.newPage();
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`${base}/realm/${realm}/execution`, { waitUntil: "domcontentloaded" });
  await page.getByText("执行与问题闭环", { exact: false }).first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(1200);
  await selectIssue(page, openIssueTitle);
  await assertVisible(page.getByRole("button", { name: "triaged", exact: true }), "triaged action");
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(outDir, "V10.6-R4-REAL-01-issue-workbench.png") });

  await selectIssue(page, issueTitle);
  await assertVisible(page.getByText("业务 Skill 草稿", { exact: false }).first(), "skill section");
  const expectedOutput = page.getByPlaceholder("预期输出");
  await assertVisible(expectedOutput, "skill expected output editor");
  const skillNameInput = page.getByPlaceholder("Skill 名称");
  await assertVisible(skillNameInput, "skill name editor");
  await expectedOutput.scrollIntoViewIfNeeded();
  await page.waitForTimeout(400);
  const skillBox = await expectedOutput.boundingBox();
  if (!skillBox || skillBox.y < 0 || skillBox.y > 900) {
    throw new Error(`skill editor not in viewport: ${JSON.stringify(skillBox)}`);
  }
  await page.screenshot({ path: path.join(outDir, "V10.6-R4-REAL-02-skill-draft.png") });
  if (errors.length > 0) {
    throw new Error(`owner page console errors: ${errors.join(" | ")}`);
  }
  await context.close();

  const narrow = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await narrow.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: token });
  const narrowPage = await narrow.newPage();
  await narrowPage.goto(`${base}/realm/${realm}/execution`, { waitUntil: "domcontentloaded" });
  await narrowPage.getByText("执行与问题闭环", { exact: false }).first().waitFor({ timeout: 20000 });
  await narrowPage.waitForTimeout(1200);
  await selectIssue(narrowPage, issueTitle);
  const overflow = await narrowPage.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  if (overflow.scrollWidth > overflow.clientWidth + 1) {
    throw new Error(`narrow overflow: ${overflow.scrollWidth} > ${overflow.clientWidth}`);
  }
  await narrowPage.screenshot({ path: path.join(outDir, "V10.6-R4-REAL-03-narrow-responsive.png"), fullPage: true });
  await narrow.close();

  const denied = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await denied.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: outsiderToken });
  const deniedPage = await denied.newPage();
  await deniedPage.goto(`${base}/realm/${realm}/execution`, { waitUntil: "domcontentloaded" });
  await assertVisible(deniedPage.getByText("无权限", { exact: false }).first(), "no permission state");
  await deniedPage.waitForTimeout(800);
  await deniedPage.screenshot({ path: path.join(outDir, "V10.6-R4-REAL-04-no-permission.png") });
  await denied.close();
  console.log(`PASS saved r4 real screenshots errors=0`);
} finally {
  await browser.close();
}
