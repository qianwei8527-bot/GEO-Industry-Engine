import { test } from "node:test";
import assert from "node:assert/strict";
import {
  EMPTY_PUBLIC_INTAKE_FORM,
  formatFileSize,
  validatePublicIntake,
} from "../../src/lib/public-intake/form";
import type { PublicIntakeFormValues } from "../../src/lib/public-intake/types";

const CONTEXT = {
  allowed_file_types: [".pdf", ".txt", ".md"],
  max_files: 5,
  max_file_bytes: 10 * 1024 * 1024,
};

function filledForm(overrides: Partial<PublicIntakeFormValues> = {}): PublicIntakeFormValues {
  return {
    ...EMPTY_PUBLIC_INTAKE_FORM,
    enterpriseName: "深圳市恒域世界科技有限公司",
    relationship: "企业自身",
    problem: "从零开始建立 GEO 认知",
    consentDataAnalysis: true,
    consentUseAuthorization: true,
    serverStagingConsent: true,
    ...overrides,
  };
}

test("public intake validation requires name, relationship, problem and consent", () => {
  const errors = validatePublicIntake(EMPTY_PUBLIC_INTAKE_FORM, CONTEXT, []);
  assert.ok(errors.names);
  assert.ok(errors.relationship);
  assert.ok(errors.problem);
  assert.ok(errors.consent);
});

test("public intake validation accepts a real filled form", () => {
  const errors = validatePublicIntake(filledForm(), CONTEXT, []);
  assert.deepEqual(errors, {});
});

test("public intake validation rejects unsupported type and oversized files", () => {
  const unsupported = new File(["x"], "notes.exe", { type: "application/octet-stream" });
  const errors = validatePublicIntake(filledForm(), CONTEXT, [unsupported]);
  assert.match(errors.files || "", /不支持文件类型/);

  const oversized = new File(["x".repeat(11 * 1024 * 1024)], "big.txt", { type: "text/plain" });
  const sizeErrors = validatePublicIntake(filledForm(), CONTEXT, [oversized]);
  assert.match(sizeErrors.files || "", /超过大小限制/);
});

test("formatFileSize keeps values readable", () => {
  assert.equal(formatFileSize(0), "0 B");
  assert.equal(formatFileSize(1024), "1.0 KB");
  assert.equal(formatFileSize(10 * 1024 * 1024), "10 MB");
});
