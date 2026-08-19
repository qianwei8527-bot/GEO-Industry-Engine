import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}

const base = process.env.V106_R4_REAL_BASE || "http://localhost:3109";
const realm = process.env.V106_R4_REAL_REALM;
const token = process.env.V106_R4_REAL_TOKEN;
const projectId = process.env.V106_R4_REAL_PROJECT_ID;
const workItemId = process.env.V106_R4_REAL_TASK_ID;
const skilllessIssueTitle = process.env.V106_R4_REAL_SKILLLESS_ISSUE_TITLE || "工具调用超时";
const verifiedIssueTitle = process.env.V106_R4_REAL_ISSUE_TITLE || "发布渠道权限不足";
if (!realm || !token || !projectId || !workItemId) {
  throw new Error("set V106_R4_REAL_REALM, V106_R4_REAL_TOKEN, V106_R4_REAL_PROJECT_ID and V106_R4_REAL_TASK_ID");
}

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

async function api(page, path, options = {}) {
  return page.evaluate(
    async ({ path, options }) => {
      const token = localStorage.getItem("geo_token") || "";
      const headers = { Authorization: `Bearer ${token}` };
      if (options.body !== undefined) headers["Content-Type"] = "application/json";
      const res = await fetch(path, { ...options, headers });
      let data = null;
      try {
        data = await res.json();
      } catch {
        // non-json
      }
      return { status: res.status, data };
    },
    { path, options },
  );
}

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await context.addInitScript(({ value }) => localStorage.setItem("geo_token", value), { value: token });
  const page = await context.newPage();
  const pageErrors = [];
  const failedResponses = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 500) failedResponses.push(`${response.status()} ${response.url()}`);
  });

  async function assertVisible(locator, label) {
    await locator.waitFor({ state: "visible", timeout: 20000 });
    if (!(await locator.isVisible())) throw new Error(`${label} is not visible`);
  }

  async function selectIssue(title) {
    const row = page.locator("button").filter({ hasText: title }).first();
    await assertVisible(row, `issue row ${title}`);
    await row.click();
    const detail = page.locator("div.rounded-md.border.border-slate-200.bg-white.p-3").filter({ hasText: title }).first();
    await assertVisible(detail, `issue detail ${title}`);
  }

  await page.goto(`${base}/realm/${realm}/execution`, { waitUntil: "domcontentloaded" });
  await page.getByText("执行与问题闭环", { exact: false }).first().waitFor({ timeout: 30000 });
  await page.waitForTimeout(1200);

  await selectIssue(skilllessIssueTitle);
  const generateButton = page.getByRole("button", { name: "生成 Skill 草稿" });
  await assertVisible(generateButton, "skill generate button on verified issue");
  await generateButton.click();
  await page.getByText("Skill 草稿已生成，等待域主确认", { exact: false }).first().waitFor({ timeout: 20000 });

  const newestDraft = page.locator("div.rounded-md.bg-slate-50").filter({ hasText: "问题处理 Skill 草稿" }).first();
  await assertVisible(newestDraft, "newest skill draft");
  const outputInput = newestDraft.getByPlaceholder("预期输出");
  await assertVisible(outputInput, "skill output editor");
  await outputInput.fill("工具超时后的重试与降级处理方案");
  await newestDraft.getByRole("button", { name: "保存" }).click();
  await page.getByText("Skill 草稿已保存为新版本", { exact: false }).first().waitFor({ timeout: 20000 });

  const skillList = await api(page, `/api/v1/issues/skills?realm_id=${realm}`);
  if (skillList.status !== 200 || !Array.isArray(skillList.data?.skills) || skillList.data.skills.length < 2) {
    throw new Error(`skill list invalid: ${JSON.stringify(skillList).slice(0, 500)}`);
  }
  const newestSkill = skillList.data.skills[0];
  if (newestSkill.status !== "draft") throw new Error("newest skill should be draft");
  const stalePatch = await api(page, `/api/v1/issues/skills/${newestSkill.id}`, {
    method: "PATCH",
    body: JSON.stringify({ edits: { expected_output: "旧版本覆盖" }, expected_version: 1 }),
  });
  if (stalePatch.status !== 400) throw new Error(`stale skill version patch should be 400, got ${stalePatch.status}`);

  const refreshedDraft = page.locator("div.rounded-md.bg-slate-50").filter({ hasText: "问题处理 Skill 草稿" }).first();
  await assertVisible(refreshedDraft, "refreshed skill draft");
  await refreshedDraft.getByRole("button", { name: "确认" }).click();
  await page.getByText("Skill 草稿已确认沉淀", { exact: false }).first().waitFor({ timeout: 20000 });
  const confirmedRow = page.locator("div.rounded-md.bg-slate-50").filter({ hasText: "confirmed" }).first();
  await assertVisible(confirmedRow, "confirmed skill row");
  if ((await confirmedRow.getByRole("button", { name: "保存" }).count()) !== 0) {
    throw new Error("confirmed skill still has edit button");
  }
  if ((await confirmedRow.getByPlaceholder("预期输出").count()) !== 0) {
    throw new Error("confirmed skill still has output editor");
  }

  await selectIssue(verifiedIssueTitle);
  if ((await page.getByRole("button", { name: "triaged", exact: true }).count()) !== 0) {
    throw new Error("terminal issue still exposes triaged action");
  }
  await assertVisible(page.getByRole("button", { name: "生成 Skill 草稿" }), "skill button on verified terminal issue");

  const rejectedCreate = await api(page, "/api/v1/issues", {
    method: "POST",
    body: JSON.stringify({ realm_id: realm, original_text: "x", truth_scope: "verified" }),
  });
  if (rejectedCreate.status !== 400 || !JSON.stringify(rejectedCreate.data).includes("observed")) {
    throw new Error(`create with verified should be 400, got ${JSON.stringify(rejectedCreate)}`);
  }

  const clientKey = `issue-e2e-${Date.now()}`;
  const payload = {
    realm_id: realm,
    project_id: projectId,
    work_item_id: workItemId,
    source_type: "plan_task",
    original_text: "幂等链路验证",
    idempotency_key: clientKey,
  };
  const firstCreate = await api(page, "/api/v1/issues", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  const secondCreate = await api(page, "/api/v1/issues", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (firstCreate.status !== 200 || secondCreate.status !== 200) {
    throw new Error(`idempotent create failed: ${JSON.stringify(firstCreate)} ${JSON.stringify(secondCreate)}`);
  }
  if (firstCreate.data.id !== secondCreate.data.id) {
    throw new Error("same client key must return same issue");
  }
  if (typeof firstCreate.data.idempotency_key !== "string" || firstCreate.data.idempotency_key.length !== 64) {
    throw new Error(`idempotency key must be 64 chars, got ${JSON.stringify(firstCreate.data.idempotency_key)}`);
  }
  if (pageErrors.length > 0 || failedResponses.length > 0) {
    throw new Error(`page errors: ${pageErrors.join(" | ")}; failed responses: ${failedResponses.join(" | ")}`);
  }

  console.log("PASS e2e r4 fix2 generate=ok edit=ok staleVersion=400 confirm=ok terminalReadonly=ok verifiedCreate=400 idempotencyHash=64 pageErrors=0 failed5xx=0");
  await context.close();
} finally {
  await browser.close();
}
