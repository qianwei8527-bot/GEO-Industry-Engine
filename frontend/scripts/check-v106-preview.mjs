import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
import { readFileSync } from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const previewPath = path.resolve("..", "docs", "v106-all-pages-design-preview.html");
const html = readFileSync(previewPath, "utf8");
const registry = JSON.parse(readFileSync(path.resolve("..", "config", "panorama", "page-registry.json"), "utf8"));
const fixtureRegistry = JSON.parse(readFileSync(path.resolve("..", "config", "panorama", "fixture-registry.json"), "utf8"));
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

const errors = [];
let page;
try {
  page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("file:///" + previewPath.replace(/\\/g, "/"), { waitUntil: "load" });

  const counts = await page.evaluate(() => ({
    pages: SURFACES.flatMap((s) => s.pages).length,
    pageIds: SURFACES.flatMap((s) => s.pages.map((p) => p.id)),
    metaKeys: Object.keys(PAGE_META).length,
    metaEntries: Object.keys(PAGE_META).filter((key) => key !== "default").length,
    stateButtons: document.querySelectorAll(".state-switcher button[data-state]").length,
  }));

  if (counts.pages !== 50) throw new Error(`50 pages expected, got ${counts.pages}`);
  if (counts.metaEntries < 50) throw new Error(`page metadata incomplete: ${counts.metaEntries}`);
  const sortedPages = counts.pageIds.slice().sort();
  const sortedMeta = (await page.evaluate(() => Object.keys(PAGE_META).filter((key) => key !== "default").sort()));
  const registryIds = registry.pages.map((item) => item.page_id).sort();
  if (JSON.stringify(sortedPages) !== JSON.stringify(sortedMeta)) {
    throw new Error("page ID set and PAGE_META set are not identical");
  }
  if (JSON.stringify(sortedPages) !== JSON.stringify(registryIds)) {
    throw new Error("preview page ID set and panorama registry are not identical");
  }
  const fixtureIds = new Set(fixtureRegistry.fixtures.map((item) => item.page_id));
  const missingFixtures = registry.pages.filter((item) => !fixtureIds.has(item.page_id)).map((item) => item.page_id);
  if (missingFixtures.length > 0) throw new Error(`pages missing fixtures: ${missingFixtures.join(",")}`);
  const metaValid = await page.evaluate(() => {
    const required = ["taskId", "release", "designStatus", "implementationStatus", "dataMode", "realRoute", "featureFlag", "lastUpdated"];
    const design = ["planned", "designed", "frozen"];
    const implementation = ["not-started", "partial", "implemented", "verified", "skeleton", "acceptance_blocked"];
    const dataMode = ["mock", "fixture", "real"];
    const flags = ["open", "hidden", "reserved", "hidden/reserved"];
    const ids = Object.keys(PAGE_META).filter((key) => key !== "default");
    for (const id of ids) {
      const meta = { ...PAGE_META.default, ...PAGE_META[id] };
      for (const key of required) {
        if (!(key in meta)) return `missing ${key} for ${id}`;
      }
      if (!design.includes(meta.designStatus)) return `bad designStatus ${id}`;
      if (!implementation.includes(meta.implementationStatus)) return `bad implementationStatus ${id}`;
      if (!dataMode.includes(meta.dataMode)) return `bad dataMode ${id}`;
      if (!flags.includes(meta.featureFlag)) return `bad featureFlag ${id}`;
    }
    return true;
  });
  if (metaValid !== true) throw new Error(metaValid);
  const expectedStates = ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"];

  await page.getByRole("button", { name: "客户与定位", exact: true }).click();
  await page.waitForTimeout(50);
  const stateCount = await page.locator(".state-switcher button[data-state]").count();
  if (stateCount !== 7) throw new Error(`expected 7 customer mock states, got ${stateCount}`);
  const actualStates = await page.locator(".state-switcher button[data-state]").evaluateAll(
    (buttons) => buttons.map((button) => button.dataset.state),
  );
  if (JSON.stringify(actualStates.slice().sort()) !== JSON.stringify(expectedStates.slice().sort())) {
    throw new Error(`customer state set mismatch: ${actualStates.join(",")}`);
  }
  for (const state of ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"]) {
    await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    await page.waitForTimeout(20);
    const visible = await page.locator(`text=${state}`).first().isVisible();
    if (!visible) throw new Error(`mock state ${state} not visible`);
  }

  await page.getByRole("button", { name: "项目与计划", exact: true }).click();
  await page.waitForTimeout(50);
  const projectStateCount = await page.locator(".state-switcher button[data-state]").count();
  if (projectStateCount !== 7) throw new Error(`expected 7 project mock states, got ${projectStateCount}`);
  const projectStates = await page.locator(".state-switcher button[data-state]").evaluateAll(
    (buttons) => buttons.map((button) => button.dataset.state),
  );
  if (JSON.stringify(projectStates.slice().sort()) !== JSON.stringify(expectedStates.slice().sort())) {
    throw new Error(`project state set mismatch: ${projectStates.join(",")}`);
  }
  for (const state of ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"]) {
    await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    await page.waitForTimeout(20);
    const visible = await page.locator(`text=${state}`).first().isVisible();
    if (!visible) throw new Error(`project mock state ${state} not visible`);
  }

  await page.getByRole("button", { name: "执行与问题", exact: true }).click();
  await page.waitForTimeout(50);
  const issueStateCount = await page.locator(".state-switcher button[data-state]").count();
  if (issueStateCount !== 7) throw new Error(`expected 7 issue mock states, got ${issueStateCount}`);
  const issueStates = await page.locator(".state-switcher button[data-state]").evaluateAll(
    (buttons) => buttons.map((button) => button.dataset.state),
  );
  if (JSON.stringify(issueStates.slice().sort()) !== JSON.stringify(expectedStates.slice().sort())) {
    throw new Error(`issue state set mismatch: ${issueStates.join(",")}`);
  }
  for (const state of ["loading", "empty", "partial", "blocked", "error", "no-permission", "normal"]) {
    await page.locator(`.state-switcher button[data-state="${state}"]`).click();
    await page.waitForTimeout(20);
    const visible = await page.locator(`text=${state}`).first().isVisible();
    if (!visible) throw new Error(`issue mock state ${state} not visible`);
  }

  const forbidden = [
    "全部来自真实 API",
    "真实运行记录",
    "真实项目",
    "前端应用面",
  ];
  const found = forbidden.filter((text) => html.includes(text));
  if (found.length > 0) throw new Error(`forbidden preview wording: ${found.join(", ")}`);
  if (!html.includes("脱机设计预览 / 非生产数据 / Mock")) throw new Error("missing offline/mock label");
  if (!html.includes("内部架构设计视图")) throw new Error("missing internal architecture marker");
  if (!html.includes("恒域世界全景")) throw new Error("missing panorama entry");
  if (errors.length > 0) throw new Error(`console/page errors: ${errors.join(" | ")}`);

  const zipPath = process.env.V106_R21_ZIP;
  if (zipPath) {
    const entries = execFileSync("tar", ["-tf", zipPath], { encoding: "utf8" })
      .split(/\r?\n/)
      .filter(Boolean);
    if (entries.some((entry) => entry.includes(".env") || /token|api_key|secret/i.test(entry))) {
      throw new Error("zip contains sensitive-looking entry");
    }
    const htmlEntries = entries.filter((entry) => entry.toLowerCase().endsWith(".html"));
    if (htmlEntries.length === 0) throw new Error("zip contains no html");
    for (const entry of htmlEntries) {
      const content = execFileSync("tar", ["-xOf", zipPath, entry], { encoding: "utf8" });
      const hit = forbidden.find((text) => content.includes(text));
      if (hit) throw new Error(`zip html ${entry} contains forbidden wording: ${hit}`);
    }
  }

  const narrow = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await narrow.goto("file:///" + previewPath.replace(/\\/g, "/"), { waitUntil: "load" });
  const overflow = await narrow.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    client: document.documentElement.clientWidth,
  }));
  if (overflow.scroll > overflow.client + 1) {
    throw new Error(`narrow overflow: ${overflow.scroll} > ${overflow.client}`);
  }
  await narrow.close();

  console.log(`PASS preview pages=${counts.pages} meta=${counts.metaEntries} registry=${registry.pages.length} fixtures=${fixtureRegistry.fixtures.length} customerStates=${stateCount} projectStates=${projectStateCount} issueStates=${issueStateCount} narrow=ok zip=${zipPath ? "checked" : "none"} errors=0`);
} finally {
  await browser.close();
}
