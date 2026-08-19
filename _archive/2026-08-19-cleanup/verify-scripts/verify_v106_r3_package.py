#!/usr/bin/env python3
"""V10.6-R3 delivery package self-check."""

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

TASK_ID = "V10.6-R3-PROJECT-PLAN"

CHANGED_SOURCE_FILES = [
    "config/universe/project_plan.yaml",
    "backend/app/services/project_plan_service.py",
    "backend/app/api/v1/project_plans.py",
    "backend/app/main.py",
    "backend/tests/test_v10p6_r3_project_plan.py",
    "frontend/src/components/realm-owner/project-plan-workbench.tsx",
    "frontend/src/lib/realm-owner/r3-project-plan.ts",
    "frontend/src/components/realm-owner/realm-owner-section-page.tsx",
    "frontend/src/components/app-shell/surface-config.ts",
    "frontend/scripts/check-v106-preview.mjs",
    "frontend/scripts/capture-v106-r3-screenshots.mjs",
    "scripts/verify_v106_r3_package.py",
    "docs/17-8_V10.6-R3-project-plan-execution-report.md",
    "docs/V10.6-R3-code-change-list.md",
    "docs/v106-all-pages-design-preview.html",
    "docs/generated_images/V10.6-R3-01-projects-empty.png",
    "docs/generated_images/V10.6-R3-15-narrow-responsive.png",
    "docs/generated_images/V10.6-R3-mock-state-loading.png",
    "docs/generated_images/V10.6-R3-mock-state-empty.png",
    "docs/generated_images/V10.6-R3-mock-state-partial.png",
    "docs/generated_images/V10.6-R3-mock-state-blocked.png",
    "docs/generated_images/V10.6-R3-mock-state-error.png",
    "docs/generated_images/V10.6-R3-mock-state-no-permission.png",
    "docs/generated_images/V10.6-R3-mock-state-normal.png",
]


def ascii_path(path: str) -> bool:
    return all(ord(ch) < 128 for ch in path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "MANIFEST.md"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_bytes = manifest_path.read_bytes()

    rows = []
    for line in manifest_text.splitlines():
        match = re.match(r"^\| ([^|]+) \| ([^|]+) \| ([0-9A-F]{64}) \|$", line)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))

    if not rows:
        print("FAIL manifest rows not found")
        return 1

    errors = []
    zip_path = Path(args.zip_path)
    if not zip_path.exists():
        print("FAIL zip missing")
        return 1

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        expected_names = {row[0] for row in rows} | {"MANIFEST.md"}
        if names != expected_names:
            errors.append(f"file set mismatch: missing={sorted(expected_names - names)} extra={sorted(names - expected_names)}")
        if zf.read("MANIFEST.md") != manifest_bytes:
            errors.append("MANIFEST.md differs")
        bad_paths = [name for name in names if not ascii_path(name)]
        if bad_paths:
            errors.append(f"non-ascii paths: {bad_paths}")
        for zip_entry, source_rel, expected_hash in rows:
            source_path = root / source_rel
            if not source_path.exists() or sha256_bytes(source_path.read_bytes()) != expected_hash:
                errors.append(f"source hash mismatch: {source_rel}")
            if zip_entry not in names or sha256_bytes(zf.read(zip_entry)) != expected_hash:
                errors.append(f"zip hash mismatch: {zip_entry}")
        sensitive = [
            name for name in names
            if ".env" in name.lower()
            or re.search(r"token|api[_-]?key|secret", name, re.IGNORECASE)
        ]
        if sensitive:
            errors.append(f"sensitive entries: {sensitive}")
        preview = zf.read("docs/v106-all-pages-design-preview.html").decode("utf-8")
        if TASK_ID not in preview:
            errors.append(f"taskId {TASK_ID} not found in preview")
        source_paths = {row[1] for row in rows}
        missing_changed = [rel for rel in CHANGED_SOURCE_FILES if rel not in source_paths]
        if missing_changed:
            errors.append(f"changed files missing: {missing_changed}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PASS entries={len(names)} rows={len(rows)} ascii=ok hashes=ok changed=ok taskId=ok sensitive=0"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
