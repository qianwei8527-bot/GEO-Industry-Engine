#!/usr/bin/env python3
"""Panorama skeleton registry integrity check."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {"workbench", "list", "detail", "config", "management", "canvas"}
FLAGS = {"open", "hidden", "reserved", "hidden/reserved"}
STATUSES = {"skeleton", "implemented", "acceptance_blocked", "not-started", "partial", "verified"}
SURFACES = {"panorama", "owner", "public", "operations", "governance", "midplatform", "backend"}
FIXTURE_FIELDS = {
    "fixture_id",
    "application_surface",
    "page_id",
    "realm_id",
    "project_id",
    "user_role",
    "truth_scope",
    "scenario",
    "data_mode",
    "generated_at",
    "source_label",
    "simulation_marker",
    "no_real_write",
}


def main() -> int:
    errors = []
    registry = json.loads((ROOT / "config" / "panorama" / "page-registry.json").read_text(encoding="utf-8"))
    fixtures = json.loads((ROOT / "config" / "panorama" / "fixture-registry.json").read_text(encoding="utf-8"))
    capabilities = json.loads((ROOT / "config" / "panorama" / "capability-map.json").read_text(encoding="utf-8"))

    pages = registry["pages"]
    fixture_pages = {item["page_id"] for item in fixtures["fixtures"]}
    if len(pages) != 50:
        errors.append(f"expected 50 pages, got {len(pages)}")
    if len(fixtures["fixtures"]) != 50:
        errors.append(f"expected 50 fixtures, got {len(fixtures['fixtures'])}")
    missing = [page["page_id"] for page in pages if page["page_id"] not in fixture_pages]
    if missing:
        errors.append(f"pages missing fixtures: {missing}")
    extra = [page_id for page_id in fixture_pages if page_id not in {page["page_id"] for page in pages}]
    if extra:
        errors.append(f"fixtures without pages: {extra}")

    capability_ids = {item["capability_id"] for item in capabilities["midplatforms"]}
    capability_ids.update({item["base_id"] for item in capabilities["bases"]})
    for page in pages:
        if page["application_surface"] not in SURFACES:
            errors.append(f"bad surface {page['page_id']}")
        if page["template"] not in TEMPLATES:
            errors.append(f"bad template {page['page_id']}: {page['template']}")
        if page["feature_flag"] not in FLAGS:
            errors.append(f"bad flag {page['page_id']}: {page['feature_flag']}")
        if page["implementation_status"] not in STATUSES:
            errors.append(f"bad status {page['page_id']}: {page['implementation_status']}")
        if page["page_id"] in capabilities["page_to_capability"]:
            missing_cap = [cid for cid in capabilities["page_to_capability"][page["page_id"]] if cid not in capability_ids]
            if missing_cap:
                errors.append(f"missing capabilities for {page['page_id']}: {missing_cap}")

    for fixture in fixtures["fixtures"]:
        missing_fields = FIXTURE_FIELDS - set(fixture)
        if missing_fields:
            errors.append(f"fixture {fixture['fixture_id']} missing fields: {sorted(missing_fields)}")
        if not fixture.get("simulation_marker"):
            errors.append(f"fixture {fixture['fixture_id']} must set simulation_marker")
        if not fixture.get("no_real_write"):
            errors.append(f"fixture {fixture['fixture_id']} must set no_real_write")
        if fixture.get("data_mode") != "fixture":
            errors.append(f"fixture {fixture['fixture_id']} data_mode must be fixture")

    if len(capabilities["midplatforms"]) != 10:
        errors.append(f"expected 10 midplatforms, got {len(capabilities['midplatforms'])}")
    if len(capabilities["bases"]) != 3:
        errors.append(f"expected 3 bases, got {len(capabilities['bases'])}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"PASS pages={len(pages)} fixtures={len(fixtures['fixtures'])} midplatforms={len(capabilities['midplatforms'])} "
        f"bases={len(capabilities['bases'])} surfaces=ok templates=ok statuses=ok"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
