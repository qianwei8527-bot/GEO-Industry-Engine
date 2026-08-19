import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const BASE = process.env.V106_BASE_URL || "http://localhost:3106";
const CHROME = process.env.CHROME_PATH;
if (!process.env.CHROME_PATH || !process.env.PLAYWRIGHT_PATH) {
  throw new Error("set CHROME_PATH and PLAYWRIGHT_PATH");
}
const ownerToken = process.env.V106_OWNER_TOKEN || "";
const realmId = process.env.V106_REALM_ID || "";
const validToken = process.env.V106_VALID_TOKEN || "";
const narrowToken = process.env.V106_NARROW_TOKEN || "";
const submitToken = process.env.V106_SUBMIT_TOKEN || "";

if (!ownerToken || !realmId || !validToken || !narrowToken) {
  throw new Error("set V106_OWNER_TOKEN, V106_REALM_ID, V106_VALID_TOKEN and V106_NARROW_TOKEN");
}

const browser = await chromium.launch({
  executablePath: CHROME,
  headless: true,
  args: ["--disable-gpu", "--no-sandbox"],
});

async function checkPage(name, url, options = {}) {
  const context = await browser.newContext({
    viewport: options.viewport || { width: 1440, height: 900 },
  });
  if (options.token) {
    await context.addInitScript(
      ({ token }) => localStorage.setItem("geo_token", token),
      { token: options.token },
    );
  }
  const page = await context.newPage();
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      const text = message.text();
      const expectedResourceError = options.allowResourceErrors && text.includes("status of 401");
      if (!expectedResourceError) errors.push(text);
    }
  });
  page.on("pageerror", (error) => {
    if (!options.allowPageErrors) errors.push(error.message);
  });
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.locator(options.selector).waitFor({ timeout: 20000 });
  await page.waitForTimeout(600);
  const metrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
    shellSurface: document.querySelector("[data-application-surface]")?.getAttribute("data-application-surface") || null,
    bodyText: document.body.innerText,
  }));
  const horizontalOverflow = metrics.scrollWidth > metrics.clientWidth + 1 || metrics.bodyScrollWidth > metrics.clientWidth + 1;
  const fullTokenLeak = Boolean(
    options.forbidFullToken && /AUTH-[A-Za-z0-9_-]{20,}/.test(metrics.bodyText),
  );
  const pass = errors.length === 0 && !horizontalOverflow && metrics.shellSurface !== null && !fullTokenLeak;
  if (horizontalOverflow) {
    const offenders = await page.evaluate(() =>
      Array.from(document.querySelectorAll("body *"))
        .filter((el) => {
          const box = el.getBoundingClientRect();
          return box.right > window.innerWidth + 1 && box.width > 0;
        })
        .slice(0, 6)
        .map((el) => `${el.tagName.toLowerCase()}.${String(el.className).slice(0, 80)}`),
    );
    console.log("overflow elements:", offenders.join(" | "));
  }
  console.log(
    `${pass ? "PASS" : "FAIL"} ${name} surface=${metrics.shellSurface} overflow=${horizontalOverflow} fullTokenLeak=${fullTokenLeak} errors=${errors.length}`,
  );
  if (errors.length) console.log(errors.join("\n"));
  await context.close();
  return pass;
}

try {
  const results = await Promise.all([
    checkPage("owner", `${BASE}/realm/${realmId}/explore`, {
      token: ownerToken,
      selector: 'role=heading[name="域主工作台"]',
      forbidFullToken: true,
    }),
    checkPage("public-empty", `${BASE}/intake/${validToken}`, {
      selector: 'text=提交客户资料',
    }),
    checkPage("public-invalid", `${BASE}/intake/AUTH-NOT-VALID-0001`, {
      selector: 'text=无权使用该提交入口',
      allowResourceErrors: true,
    }),
    checkPage("public-narrow", `${BASE}/intake/${narrowToken}`, {
      viewport: { width: 390, height: 844 },
      selector: 'text=提交客户资料',
    }),
  ]);
  if (results.some((result) => !result)) process.exitCode = 1;

  if (submitToken) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    page.on("console", (message) => {
      if (message.type() === "error") errors.push(message.text());
    });
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(`${BASE}/intake/${submitToken}`, { waitUntil: "domcontentloaded" });
    await page.getByRole("heading", { name: "资料已提交" }).waitFor({ timeout: 20000 });
    await page.waitForTimeout(800);
    const rect = await page.getByRole("heading", { name: "资料已提交" }).evaluate((element) => {
      const box = element.getBoundingClientRect();
      return { top: box.top, bottom: box.bottom, height: window.innerHeight };
    });
    const visible = rect.top >= 0 && rect.bottom <= rect.height;
    const chineseVisible = await page.getByText("截图验收企业域").count() > 0;
    const unknownVisible = await page.getByText(/需要补充资料/).count() > 0;
    const pass = visible && chineseVisible && unknownVisible && errors.length === 0;
    console.log(`${pass ? "PASS" : "FAIL"} submitted-result visible=${visible} chinese=${chineseVisible} unknown=${unknownVisible} errors=${errors.length}`);
    if (!pass) process.exitCode = 1;
    await context.close();
  }
} finally {
  await browser.close();
}
