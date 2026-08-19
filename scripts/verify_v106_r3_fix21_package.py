#!/usr/bin/env python3
"""V10.6-R3-FIX2.1 package self-check, runnable from extracted ZIP directory."""

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

TASK_ID = "V10.6-R3-FIX2.1-FINAL-FREEZE"

CHANGED_ZIP_FILES = [
    "backend/app/services/project_plan_service.py",
    "backend/tests/test_v10p6_r3_project_plan.py",
    "frontend/src/lib/realm-owner/r3-project-plan.ts",
    "frontend/src/components/realm-owner/project-plan-workbench.tsx",
    "frontend/tests/realm-owner-home/r3-project-plan.test.ts",
    "frontend/scripts/capture-v106-r3-real-screenshots.mjs",
    "docs/v106-all-pages-design-preview.html",
    "docs/18-1_V10.6-R3-FIX2.1-final-freeze-report.md",
    "docs/V10.6-R3-code-change-list.md",
    "scripts/verify_v106_r3_fix21_package.py",
    "docs/generated_images/V10.6-R3-REAL-01-projects-page.png",
    "docs/generated_images/V10.6-R3-REAL-02-tasks-progress-overdue.png",
    "docs/generated_images/V10.6-R3-REAL-03-narrow-responsive.png",
    "docs/generated_images/V10.6-R3-REAL-04-no-permission.png",
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
    if not manifest_path.exists():
        print("FAIL MANIFEST.md not found next to scripts/")
        return 1
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_bytes = manifest_path.read_bytes()

    rows = []
    for line in manifest_text.splitlines():
        match = re.match(r"^\| ([^|]+) \| ([^|]+) \| ([0-9A-F]{64}) \|$", line)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))

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
        for zip_entry, _source_rel, expected_hash in rows:
            if zip_entry not in names:
                errors.append(f"missing zip entry: {zip_entry}")
                continue
            if sha256_bytes(zf.read(zip_entry)) != expected_hash:
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
        missing_changed = [rel for rel in CHANGED_ZIP_FILES if rel not in names]
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
