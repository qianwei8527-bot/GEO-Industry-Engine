import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";

const API_BASE = "http://127.0.0.1:8080/api/v1";
const WEB_BASE = process.env.V106_BASE_URL || "http://localhost:3106";
const OUT_DIR = path.resolve("..", "docs", "generated_images");
const CHROME = process.env.CHROME_PATH;
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
const OWNER_EMAIL = process.env.V106_R2_OWNER_EMAIL || "";
const OWNER_PASSWORD = process.env.V106_R2_OWNER_PASSWORD || "";

if (!OWNER_EMAIL || !OWNER_PASSWORD) {
  throw new Error("set V106_R2_OWNER_EMAIL and V106_R2_OWNER_PASSWORD");
}

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

async function api(pathname, { method = "GET", token, body, form } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) {
    payload = form;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(`${API_BASE}${pathname}`, { method, headers, body: payload });
  if (!res.ok) {
    throw new Error(`${method} ${pathname} -> ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

async function login() {
  const data = await api("/auth/login", {
    method: "POST",
    body: { email: OWNER_EMAIL, password: OWNER_PASSWORD },
  });
  return data.access_token;
}

async function createRealm(token, name) {
  const ws = await api("/realm/enterprises", {
    method: "POST",
    token,
    body: { name, website: `https://${name.toLowerCase().replace(/[^a-z0-9]/g, "")}.test` },
  });
  return ws.identity.id;
}

async function createIntake(token, realmId) {
  const form = new FormData();
  form.append("realm_id", realmId);
  form.append("relationship", "企业自身");
  form.append(
    "pasted_text",
    "品牌名称：恒域R2截图品牌\n企业主体：R2截图企业有限公司\n产品：GEO截图服务\n问题：从零开始建立GEO认知与转化路径\n转化目标：让品牌在AI搜索中被看见",
  );
  const data = await api("/intakes", { method: "POST", token, form });
  return data.id;
}

async function analyze(token, intakeId) {
  return api(`/intakes/${intakeId}/analyze`, { method: "POST", token, body: {} });
}

async function workbench(token, intakeId) {
  return api(`/intakes/${intakeId}/workbench`, { token });
}

async function startReview(token, intakeId) {
  return api(`/intakes/${intakeId}/review/start`, { method: "POST", token, body: {} });
}

async function updateProfile(token, intakeId, edits) {
  const wb = await workbench(token, intakeId);
  const version = wb.analyses[0].version;
  return api(`/intakes/${intakeId}/profile`, {
    method: "POST",
    token,
    body: { edits, expected_version: version },
  });
}

async function confirmProfile(token, intakeId) {
  const wb = await workbench(token, intakeId);
  return api(`/intakes/${intakeId}/profile/confirm`, {
    method: "POST",
    token,
    body: { edits: {}, expected_version: wb.analyses[0].version },
  });
}

async function generatePositioning(token, intakeId) {
  return api(`/intakes/${intakeId}/positioning/generate`, { method: "POST", token, body: {} });
}

async function confirmPositioning(token, intakeId) {
  const wb = await workbench(token, intakeId);
  return api(`/intakes/${intakeId}/positioning/confirm`, {
    method: "POST",
    token,
    body: { edits: {}, expected_version: wb.analyses[0].version },
  });
}

async function createProject(token, intakeId) {
  const wb = await workbench(token, intakeId);
  return api(`/intakes/${intakeId}/project`, {
    method: "POST",
    token,
    body: { confirmed: true, expected_position_version: wb.analyses[0].version },
  });
}

const browser = await chromium.launch({
  executablePath: CHROME,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

async function shot(page, name, fullPage = false) {
  await page.screenshot({ path: path.join(OUT_DIR, name), fullPage });
  console.log(`saved ${name}`);
}

async function openOwnerPage(token, realmId) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await context.addInitScript((value) => localStorage.setItem("geo_token", value), token);
  const page = await context.newPage();
  await page.goto(`${WEB_BASE}/realm/${realmId}/customers`, { waitUntil: "domcontentloaded" });
  await page.getByText("基础架构模拟闭环").waitFor({ timeout: 20000 });
  return { context, page };
}

async function selectIntake(page, code) {
  await page.getByText(code, { exact: true }).click();
  await page.getByText("当前客户档案").waitFor({ timeout: 10000 });
}

try {
  const ownerToken = await login();
  const emptyRealmId = await createRealm(ownerToken, "R2 Empty Realm");

  const realmId = process.env.V106_REALM_ID || "";
  if (!realmId) throw new Error("set V106_REALM_ID for state screenshots");

  // Create one intake per required state.
  const awaitingId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, awaitingId);

  const partialId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, partialId);

  const editId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, editId);
  await startReview(ownerToken, editId);
  await updateProfile(ownerToken, editId, { target_customer: "AI行业客户" });

  const confirmedId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, confirmedId);
  await startReview(ownerToken, confirmedId);
  await updateProfile(ownerToken, confirmedId, { target_customer: "AI行业客户" });
  await confirmProfile(ownerToken, confirmedId);

  const positionDraftId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, positionDraftId);
  await startReview(ownerToken, positionDraftId);
  await updateProfile(ownerToken, positionDraftId, { target_customer: "AI行业客户" });
  await confirmProfile(ownerToken, positionDraftId);
  await generatePositioning(ownerToken, positionDraftId);

  const positionConfirmedId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, positionConfirmedId);
  await startReview(ownerToken, positionConfirmedId);
  await updateProfile(ownerToken, positionConfirmedId, { target_customer: "AI行业客户" });
  await confirmProfile(ownerToken, positionConfirmedId);
  await generatePositioning(ownerToken, positionConfirmedId);
  await confirmPositioning(ownerToken, positionConfirmedId);

  const triggerId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, triggerId);
  await startReview(ownerToken, triggerId);
  await updateProfile(ownerToken, triggerId, { target_customer: "AI行业客户" });
  await confirmProfile(ownerToken, triggerId);
  await generatePositioning(ownerToken, triggerId);
  await confirmPositioning(ownerToken, triggerId);

  const projectId = await createIntake(ownerToken, realmId);
  await analyze(ownerToken, projectId);
  await startReview(ownerToken, projectId);
  await updateProfile(ownerToken, projectId, { target_customer: "AI行业客户" });
  await confirmProfile(ownerToken, projectId);
  await generatePositioning(ownerToken, projectId);
  await confirmPositioning(ownerToken, projectId);
  await createProject(ownerToken, projectId);

  // 1. Empty state.
  let handle = await openOwnerPage(ownerToken, emptyRealmId);
  await handle.page.getByText("尚无客户提交").waitFor({ timeout: 10000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-01-customers-empty.png");
  await handle.context.close();

  // 2. Awaiting review + 3/4. partial/unknown with source/truth.
  handle = await openOwnerPage(ownerToken, realmId);
  const awaitingCode = (await workbench(ownerToken, awaitingId)).intake_code;
  await selectIntake(handle.page, awaitingCode);
  await handle.page.getByText("待审核").first().waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-02-customers-awaiting.png");

  const partialCode = (await workbench(ownerToken, partialId)).intake_code;
  await selectIntake(handle.page, partialCode);
  await handle.page.getByText(/待补充 \d+ 项/).waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-03-profile-partial-unknown.png");
  await handle.context.close();

  // 5. Owner edit state.
  handle = await openOwnerPage(ownerToken, realmId);
  const editCode = (await workbench(ownerToken, editId)).intake_code;
  await selectIntake(handle.page, editCode);
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-05-owner-edit.png");
  await handle.context.close();

  // 6. Profile confirmed.
  handle = await openOwnerPage(ownerToken, realmId);
  const confirmedCode = (await workbench(ownerToken, confirmedId)).intake_code;
  await selectIntake(handle.page, confirmedCode);
  await handle.page.getByText("档案已确认").first().waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-06-profile-confirmed.png");
  await handle.context.close();

  // 7. Positioning draft.
  handle = await openOwnerPage(ownerToken, realmId);
  const draftCode = (await workbench(ownerToken, positionDraftId)).intake_code;
  await selectIntake(handle.page, draftCode);
  await handle.page.getByText("定位草稿").first().waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-07-positioning-draft.png");
  await handle.context.close();

  // 8. Positioning confirmed.
  handle = await openOwnerPage(ownerToken, realmId);
  const posCode = (await workbench(ownerToken, positionConfirmedId)).intake_code;
  await selectIntake(handle.page, posCode);
  await handle.page.getByText("定位已确认").first().waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-08-positioning-confirmed.png");

  // 9. Project trigger confirmation.
  const triggerCode = (await workbench(ownerToken, triggerId)).intake_code;
  await selectIntake(handle.page, triggerCode);
  await handle.page.getByRole("button", { name: "基于此定位创建项目" }).click();
  await handle.page.getByText("确认创建项目草稿").waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(300);
  await shot(handle.page, "V10.6-R2-09-project-trigger-confirm.png");
  await handle.context.close();

  // 10. Project created.
  handle = await openOwnerPage(ownerToken, realmId);
  const projectCode = (await workbench(ownerToken, projectId)).intake_code;
  await selectIntake(handle.page, projectCode);
  await handle.page.getByText("项目已建立").waitFor({ timeout: 5000 });
  await handle.page.waitForTimeout(400);
  await shot(handle.page, "V10.6-R2-10-project-created.png");
  await handle.context.close();

  // 11. No permission.
  const outsiderEmail = `r2-outsider-${Date.now()}@geotest.com`;
  const outsider = await api("/auth/register", {
    method: "POST",
    body: { email: outsiderEmail, password: "Outsider123!", name: "外部用户" },
  });
  const outsiderContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await outsiderContext.addInitScript(
    (value) => localStorage.setItem("geo_token", value),
    outsider.access_token,
  );
  const outsiderPage = await outsiderContext.newPage();
  await outsiderPage.goto(`${WEB_BASE}/realm/${emptyRealmId}/customers`, { waitUntil: "domcontentloaded" });
  await outsiderPage.getByText("无权限访问该 Realm").waitFor({ timeout: 15000 });
  await outsiderPage.waitForTimeout(400);
  await shot(outsiderPage, "V10.6-R2-11-no-permission.png");
  await outsiderContext.close();

  // 12. Narrow responsive.
  const narrowContext = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await narrowContext.addInitScript((value) => localStorage.setItem("geo_token", value), ownerToken);
  const narrowPage = await narrowContext.newPage();
  await narrowPage.goto(`${WEB_BASE}/realm/${realmId}/customers`, { waitUntil: "domcontentloaded" });
  await narrowPage.getByText("当前客户档案").waitFor({ timeout: 15000 });
  await narrowPage.waitForTimeout(500);
  await shot(narrowPage, "V10.6-R2-12-narrow-responsive.png", true);
  await narrowContext.close();
} finally {
  await browser.close();
}
