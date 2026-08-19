import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  canShowSkillButton,
  classificationNeedsConfirm,
  isTerminalIssue,
} from "../../src/lib/realm-owner/r4-issue";

describe("R4 issue UI rules", () => {
  it("shows skill button only for verified issues", () => {
    assert.equal(canShowSkillButton("verified", true), true);
    assert.equal(canShowSkillButton("open", true), false);
    assert.equal(canShowSkillButton("verified", false), false);
  });

  it("treats verified and cancelled as terminal", () => {
    assert.equal(isTerminalIssue("verified"), true);
    assert.equal(isTerminalIssue("cancelled"), true);
    assert.equal(isTerminalIssue("in_progress"), false);
  });

  it("requires owner classification confirmation for suggestions", () => {
    assert.equal(classificationNeedsConfirm("suggested"), true);
    assert.equal(classificationNeedsConfirm("confirmed"), false);
  });
});
