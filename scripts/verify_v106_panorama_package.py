#!/usr/bin/env python3
"""V10.6-PANORAMA-SKELETON-01 package self-check, runnable from extracted ZIP directory."""

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

TASK_ID = "V10.6-PANORAMA-SKELETON-01"

CHANGED_ZIP_FILES = [
    "docs/18-5_V10.6-PANORAMA-SKELETON-01-report.md",
    "docs/V10.6-PANORAMA-code-change-list.md",
    "docs/v106-all-pages-design-preview.html",
    "config/panorama/page-registry.json",
    "config/panorama/fixture-registry.json",
    "config/panorama/capability-map.json",
    "frontend/src/app/panorama/page.tsx",
    "frontend/src/components/panorama/panorama-explorer.tsx",
    "frontend/src/lib/panorama/types.ts",
    "frontend/src/components/app-shell/surface-config.ts",
    "frontend/src/components/Header.tsx",
    "frontend/scripts/check-v106-preview.mjs",
    "frontend/scripts/capture-v106-panorama-screenshots.mjs",
    "frontend/tests/operations/operations-adapter.test.ts",
    "scripts/check_v106_panorama_skeleton.py",
    "scripts/generate_v106_panorama_fixtures.py",
    "scripts/build_v106_panorama_manifest.py",
    "scripts/verify_v106_panorama_package.py",
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
            errors.append(
                f"file set mismatch: missing={sorted(expected_names - names)} extra={sorted(names - expected_names)}"
            )
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
            name
            for name in names
            if ".env" in name.lower()
            or re.search(r"token|api[_-]?key|secret", name, re.IGNORECASE)
            or ".next" in name.lower()
            or "node_modules" in name.lower()
        ]
        if sensitive:
            errors.append(f"sensitive entries: {sensitive}")
        preview = zf.read("docs/v106-all-pages-design-preview.html").decode("utf-8")
        if TASK_ID not in preview:
            errors.append(f"taskId {TASK_ID} not found in preview")
        if "acceptance_blocked" not in preview:
            errors.append("R4 acceptance_blocked marker missing in preview")
        if "恒域世界全景" not in preview:
            errors.append("panorama entry missing in preview")
        report = zf.read("docs/18-5_V10.6-PANORAMA-SKELETON-01-report.md").decode("utf-8")
        if TASK_ID not in report:
            errors.append("report does not mention task id")
        missing_changed = [rel for rel in CHANGED_ZIP_FILES if rel not in names]
        if missing_changed:
            errors.append(f"changed files missing: {missing_changed}")
        screenshot_count = len([name for name in names if name.startswith("docs/generated_images/V10.6-PANORAMA-")])
        if screenshot_count < 90:
            errors.append(f"expected at least 90 panorama screenshots, got {screenshot_count}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PASS entries={len(names)} rows={len(rows)} screenshots={screenshot_count} ascii=ok hashes=ok changed=ok taskId=ok sensitive=0"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
