import test from "node:test";
import assert from "node:assert/strict";
import { APPLICATION_SURFACES } from "../../src/components/app-shell/surface-config";

test("operations surface protocol is implemented with panorama nav", () => {
  const protocol = APPLICATION_SURFACES.operations;
  assert.equal(protocol.protocolStatus, "implemented");
  assert.equal(protocol.navItems.length, 10);
  assert.deepEqual(
    protocol.navItems.map((item) => item.id),
    ["overview", "realms", "runtime", "agents", "workflows", "connectors", "capabilities", "reports", "system", "alerts"],
  );
  assert.ok(protocol.navItems.every((item) => item.status === "open"));
});

test("governance surface protocol is implemented with panorama nav", () => {
  const protocol = APPLICATION_SURFACES.governance;
  assert.equal(protocol.protocolStatus, "implemented");
  assert.deepEqual(
    protocol.navItems.map((item) => item.id),
    ["permissions", "approvals", "realm-claims", "evidence", "external-actions", "audit", "risk", "retention", "collective"],
  );
});
