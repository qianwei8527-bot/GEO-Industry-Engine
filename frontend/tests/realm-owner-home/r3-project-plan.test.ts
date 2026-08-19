import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  ownerDefinedTemplateValid,
  planCanUpdateTask,
  buildTaskUpdatePayload,
  canSubmitTaskUpdate,
  isPlanCompleted,
  resolveSourceType,
  taskCanTransition,
  taskStatusOptions,
} from "../../src/lib/realm-owner/r3-project-plan";

describe("R3 project plan UI interaction rules", () => {
  it("enforces strict task transitions", () => {
    assert.equal(taskCanTransition("planned", "in_progress"), true);
    assert.equal(taskCanTransition("planned", "completed"), false);
    assert.equal(taskCanTransition("in_progress", "blocked"), true);
    assert.equal(taskCanTransition("blocked", "in_progress"), true);
    assert.equal(taskCanTransition("completed", "in_progress"), false);
  });

  it("disables task updates after plan completion or task completion", () => {
    assert.equal(planCanUpdateTask(true, "plan_active", "planned"), true);
    assert.equal(planCanUpdateTask(true, "plan_completed", "planned"), false);
    assert.equal(planCanUpdateTask(true, "plan_active", "completed"), false);
    assert.equal(planCanUpdateTask(false, "plan_active", "planned"), false);
  });

  it("validates owner-defined template structure", () => {
    assert.equal(ownerDefinedTemplateValid({ phases: [{ phase: "阶段一", tasks: [] }] }), true);
    assert.equal(ownerDefinedTemplateValid({ phases: [] }), false);
    assert.equal(ownerDefinedTemplateValid(null), false);
  });

  it("maps selected source to its real source_type", () => {
    const sources = [
      { source_id: "platform-seed-blank", source_type: "platform_seed" },
      { source_id: "owner-defined", source_type: "owner_defined" },
    ];
    assert.equal(resolveSourceType(sources, "platform-seed-blank"), "platform_seed");
    assert.equal(resolveSourceType(sources, "owner-defined"), "owner_defined");
    assert.equal(resolveSourceType(sources, "missing"), "platform_seed");
  });

  it("builds status options from strict transitions", () => {
    assert.deepEqual(taskStatusOptions("planned"), ["planned", "in_progress"]);
    assert.deepEqual(taskStatusOptions("in_progress"), ["in_progress", "blocked", "completed"]);
    assert.deepEqual(taskStatusOptions("completed"), ["completed"]);
  });

  it("builds real update payloads for slider and completed transitions", () => {
    const planned = { status: "planned", progress: 0, task_version: 1 };
    const inProgress = { status: "in_progress", progress: 50, task_version: 2 };
    assert.deepEqual(buildTaskUpdatePayload(planned, { progress: 50 }, 1), {
      progress: 50,
      expected_version: 1,
      expected_task_version: 1,
    });
    assert.deepEqual(buildTaskUpdatePayload(inProgress, { progress: 100 }, 1), {
      progress: 100,
      expected_version: 1,
      expected_task_version: 2,
    });
    assert.deepEqual(buildTaskUpdatePayload(inProgress, { status: "completed" }, 1), {
      status: "completed",
      progress: 100,
      expected_version: 1,
      expected_task_version: 2,
    });
  });

  it("blocks duplicate task updates while busy and detects plan completion", () => {
    assert.equal(canSubmitTaskUpdate(null, "task-1"), true);
    assert.equal(canSubmitTaskUpdate("task-1", "task-1"), false);
    assert.equal(canSubmitTaskUpdate("task-1", "task-2"), true);
    assert.equal(isPlanCompleted([{ status: "completed" }, { status: "completed" }]), true);
    assert.equal(isPlanCompleted([{ status: "completed" }, { status: "in_progress" }]), false);
    assert.equal(isPlanCompleted([]), false);
  });
});
