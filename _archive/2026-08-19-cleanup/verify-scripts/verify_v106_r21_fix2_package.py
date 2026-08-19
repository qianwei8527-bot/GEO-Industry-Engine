#!/usr/bin/env python3
"""V10.6-R2.1-FIX2 delivery package self-check.

Verifies the ZIP against MANIFEST.md:
- exact file set
- SHA-256 of every source file and every ZIP entry
- ASCII-only ZIP paths
- no sensitive-looking entries
- owner-customers preview metadata taskId
- every declared changed file is included
"""

import argparse
import hashlib
import os
import re
import sys
import zipfile
from pathlib import Path

TASK_ID = "V10.6-R2.1-FIX2-FINAL-FREEZE"

CHANGED_SOURCE_FILES = [
    "MANIFEST.md",
    "docs/17-7_V10.6-R2.1-FIX2-final-freeze-report.md",
    "docs/17-6_V10.6-R2.1-FIX1验收修正执行报告.md",
    "docs/V10.6-R2.1-代码变更清单.md",
    "docs/v106-all-pages-design-preview.html",
    "docs/generated_images/V10.6-R2.1-mock-state-blocked.png",
    "docs/generated_images/V10.6-R2.1-mock-state-empty.png",
    "docs/generated_images/V10.6-R2.1-mock-state-error.png",
    "docs/generated_images/V10.6-R2.1-mock-state-loading.png",
    "docs/generated_images/V10.6-R2.1-mock-state-no-permission.png",
    "docs/generated_images/V10.6-R2.1-mock-state-normal.png",
    "docs/generated_images/V10.6-R2.1-mock-state-partial.png",
    "scripts/verify_v106_r21_fix2_package.py",
    "backend/app/services/geo_project_service.py",
    "backend/app/services/intake_service.py",
    "backend/app/services/governance.py",
    "backend/tests/test_v10p6_r2_client_positioning.py",
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
        errors.append(f"zip missing: {zip_path}")
        return 1

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        expected_names = {row[0] for row in rows} | {"MANIFEST.md"}
        if names != expected_names:
            missing = sorted(expected_names - names)
            extra = sorted(names - expected_names)
            if missing:
                errors.append(f"missing zip entries: {missing}")
            if extra:
                errors.append(f"extra zip entries: {extra}")

        manifest_in_zip = zf.read("MANIFEST.md")
        if manifest_in_zip != manifest_bytes:
            errors.append("MANIFEST.md inside zip differs from repository file")

        bad_paths = [name for name in names if not ascii_path(name)]
        if bad_paths:
            errors.append(f"non-ASCII zip paths: {bad_paths}")

        for zip_entry, source_rel, expected_hash in rows:
            source_path = root / source_rel
            if not source_path.exists():
                errors.append(f"source missing: {source_rel}")
                continue
            actual_source = sha256_bytes(source_path.read_bytes())
            if actual_source != expected_hash:
                errors.append(f"source hash mismatch: {source_rel}")
            if zip_entry not in names:
                errors.append(f"zip entry missing: {zip_entry}")
                continue
            actual_entry = sha256_bytes(zf.read(zip_entry))
            if actual_entry != expected_hash:
                errors.append(f"zip entry hash mismatch: {zip_entry}")
            if not ascii_path(zip_entry):
                errors.append(f"non-ASCII manifest zip path: {zip_entry}")

        sensitive = [
            name for name in names
            if ".env" in name.lower()
            or re.search(r"token|api[_-]?key|secret", name, re.IGNORECASE)
        ]
        if sensitive:
            errors.append(f"sensitive-looking zip entries: {sensitive}")

        preview = zf.read("docs/v106-all-pages-design-preview.html").decode("utf-8")
        if TASK_ID not in preview:
            errors.append(f"preview taskId {TASK_ID} not found")

        manifest_source_paths = {row[1] for row in rows}
        missing_changed = [
            rel for rel in CHANGED_SOURCE_FILES
            if rel != "MANIFEST.md" and rel not in manifest_source_paths
        ]
        if missing_changed:
            errors.append(f"changed files missing from manifest: {missing_changed}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PASS zip={zip_path.name} entries={len(names)} rows={len(rows)} "
        f"ascii=ok hashes=ok changed=ok taskId=ok sensitive=0"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
