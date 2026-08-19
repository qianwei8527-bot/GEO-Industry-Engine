import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

const BASE = process.env.V106_BASE_URL || "http://localhost:3106";
const OUT_DIR = path.resolve("..", "docs", "generated_images");
const CHROME = process.env.CHROME_PATH;
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}

const ownerToken = process.env.V106_OWNER_TOKEN || "";
const realmId = process.env.V106_REALM_ID || "";
const validToken = process.env.V106_VALID_TOKEN || "";
const narrowToken = process.env.V106_NARROW_TOKEN || "";
const invalidToken = "AUTH-NOT-VALID-0001";

if (!ownerToken || !realmId || !validToken || !narrowToken) {
  throw new Error("set V106_OWNER_TOKEN, V106_REALM_ID, V106_VALID_TOKEN and V106_NARROW_TOKEN");
}

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

const fixturePath = path.join(OUT_DIR, "v106-intake-fixture.txt");
writeFileSync(
  fixturePath,
  "品牌名称：恒域世界\n企业主体：深圳市恒域世界科技有限公司\n产品：GEO运营服务\n问题：从零开始建立GEO认知\n",
  "utf8",
);

const browser = await chromium.launch({
  executablePath: CHROME,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

async function shot(page, name, fullPage = false) {
  await page.screenshot({ path: path.join(OUT_DIR, name), fullPage });
  console.log(`saved ${name}`);
}

async function newContext(width, height) {
  return browser.newContext({
    viewport: { width, height },
    deviceScaleFactor: 1,
  });
}

try {
  // 1. Owner workbench under the unified shell.
  const ownerContext = await newContext(1440, 900);
  await ownerContext.addInitScript(
    ({ token }) => localStorage.setItem("geo_token", token),
    { token: ownerToken },
  );
  const ownerPage = await ownerContext.newPage();
  await ownerPage.goto(`${BASE}/realm/${realmId}/explore`, { waitUntil: "domcontentloaded" });
  await ownerPage.getByRole("heading", { name: "域主工作台" }).waitFor({ timeout: 20000 });
  await ownerPage.getByText("公共资料提交入口").waitFor({ timeout: 10000 });
  await ownerPage.waitForTimeout(1200);
  await shot(ownerPage, "V10.6-R1-01-owner-unified-shell.png");
  await ownerContext.close();

  // 1b. Simulation closed loop on customers page.
  const simContext = await newContext(1440, 900);
  await simContext.addInitScript(
    ({ token }) => localStorage.setItem("geo_token", token),
    { token: ownerToken },
  );
  const simPage = await simContext.newPage();
  await simPage.goto(`${BASE}/realm/${realmId}/customers`, { waitUntil: "domcontentloaded" });
  await simPage.getByText("基础架构模拟闭环").waitFor({ timeout: 20000 });
  await simPage.waitForTimeout(800);
  await shot(simPage, "V10.6-R1-08-simulation-loop.png");
  await simContext.close();

  // 2. Public intake empty state.
  const emptyContext = await newContext(1440, 900);
  const emptyPage = await emptyContext.newPage();
  await emptyPage.goto(`${BASE}/intake/${validToken}`, { waitUntil: "domcontentloaded" });
  await emptyPage.getByRole("heading", { name: /提交客户资料/ }).waitFor({ timeout: 20000 });
  await emptyPage.waitForTimeout(500);
  await shot(emptyPage, "V10.6-R1-02-public-intake-empty.png");

  // 3. Filled state with file and consent.
  await emptyPage.locator('input[placeholder="企业或主体名称"]').fill("深圳市恒域世界科技有限公司");
  await emptyPage.locator('input[placeholder="品牌名称"]').fill("恒域世界");
  await emptyPage.locator('input[placeholder="核心产品或项目名称"]').fill("GEO 运营服务");
  await emptyPage.getByRole("combobox").selectOption({ label: "企业自身" });
  await emptyPage.locator('textarea[placeholder="描述最想解决的业务问题"]').fill("从零开始建立 GEO 认知与转化路径");
  await emptyPage.locator('input[placeholder="https://example.com"]').fill("https://www.example.com");
  await emptyPage.setInputFiles('input[type="file"]', fixturePath);
  await emptyPage.getByText("同意对提交资料进行数据分析和结构化提取").locator("input").check();
  await emptyPage.getByText("同意授权目标域主在项目范围内使用该资料").locator("input").check();
  await emptyPage.getByText("同意将草稿和文件暂存到目标域服务器").locator("input").check();
  await emptyPage.waitForTimeout(400);
  await shot(emptyPage, "V10.6-R1-03-public-intake-filled.png");

  // 4. Submitted / real processing result.
  await emptyPage.getByRole("button", { name: "提交分析" }).click();
  await emptyPage.getByRole("heading", { name: "资料已提交" }).waitFor({ timeout: 20000 });
  await emptyPage.waitForTimeout(600);
  await shot(emptyPage, "V10.6-R1-04-public-intake-submitted.png");
  await emptyContext.close();

  // 5. Blocked / AI key missing state (fresh token before submission).
  const blockedContext = await newContext(1440, 900);
  const blockedPage = await blockedContext.newPage();
  await blockedPage.goto(`${BASE}/intake/${narrowToken}`, { waitUntil: "domcontentloaded" });
  await blockedPage.getByText("外部 AI 未配置").waitFor({ timeout: 20000 });
  await blockedPage.waitForTimeout(500);
  await shot(blockedPage, "V10.6-R1-05-partial-ai-missing.png");
  await blockedContext.close();

  // 6. Invalid token / no permission.
  const invalidContext = await newContext(1440, 900);
  const invalidPage = await invalidContext.newPage();
  await invalidPage.goto(`${BASE}/intake/${invalidToken}`, { waitUntil: "domcontentloaded" });
  await invalidPage.getByText("无权使用该提交入口").waitFor({ timeout: 20000 });
  await shot(invalidPage, "V10.6-R1-06-token-invalid.png");
  await invalidContext.close();

  // 7. Narrow responsive state.
  const narrowContext = await newContext(390, 844);
  const narrowPage = await narrowContext.newPage();
  await narrowPage.goto(`${BASE}/intake/${narrowToken}`, { waitUntil: "domcontentloaded" });
  await narrowPage.getByRole("heading", { name: /提交客户资料/ }).waitFor({ timeout: 20000 });
  await narrowPage.waitForTimeout(500);
  await shot(narrowPage, "V10.6-R1-07-narrow-responsive.png", true);
  await narrowContext.close();
} finally {
  await browser.close();
}
