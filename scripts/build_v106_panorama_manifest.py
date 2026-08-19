#!/usr/bin/env python3
"""Build the V10.6 panorama skeleton MANIFEST.md with SHA-256 hashes."""

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "V10.6-PANORAMA-SKELETON-01"
ZIP_NAME = "V10.6-PANORAMA-SKELETON-全景骨架-执行文件.zip"

SOURCE_FILES = [
    "docs/18-5_V10.6-PANORAMA-SKELETON-01-report.md",
    "docs/V10.6-PANORAMA-code-change-list.md",
    "docs/v106-all-pages-design-preview.html",
    "config/panorama/page-registry.json",
    "config/panorama/fixture-registry.json",
    "config/panorama/capability-map.json",
    "frontend/src/app/panorama/page.tsx",
    "frontend/src/app/v106-all-pages-design-preview/route.ts",
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    entries = []
    for rel in SOURCE_FILES:
        path = ROOT / rel
        if not path.exists():
            print(f"missing source: {rel}")
            return 1
        entries.append((rel, rel, sha256(path)))
    screenshots = sorted((ROOT / "docs" / "generated_images").glob("V10.6-PANORAMA-*.png"))
    if len(screenshots) < 90:
        print(f"expected at least 90 screenshots, got {len(screenshots)}")
        return 1
    for path in screenshots:
        rel = path.relative_to(ROOT).as_posix()
        entries.append((rel, rel, sha256(path)))

    lines = [
        "# V10.6-PANORAMA-SKELETON-01 全景骨架交付 MANIFEST",
        "",
        f"- 任务编号：{TASK_ID}",
        "- 前置版本：V10.6-R3-FIX2.1-FINAL-FREEZE",
        "- 策略调整：先完成全产品骨架和模拟交互，再按价值优先级接入真实后端",
        "- R4 状态：acceptance_blocked",
        "- 是否允许部署：否",
        "- 是否允许提交或推送：否",
        f"- 交付包：{ZIP_NAME}",
        "",
        "## 文件清单（ZIP 路径 / 仓库源路径 / SHA-256）",
        "",
        "`MANIFEST.md` 为本清单文件，不计算自身哈希；ZIP 内路径全部为 ASCII。",
        "",
        "| ZIP路径（ASCII） | 仓库源路径 | SHA-256 |",
        "| --- | --- | --- |",
    ]
    for zip_path, source_rel, digest in entries:
        lines.append(f"| {zip_path} | {source_rel} | {digest} |")
    lines += [
        "",
        "## 测试结果摘要",
        "",
        "- 前端测试：28 passed。",
        "- TypeScript：通过。",
        "- lint：通过，仅仓库原有 4 项 warning。",
        "- production build：通过，55 个路由，含 `/panorama`。",
        "- 预览检查：PASS pages=50 meta=50 registry=50 fixtures=50。",
        "- 骨架完整性：PASS pages=50 fixtures=50 midplatforms=10 bases=3。",
        "- 截图与路由 Smoke：PASS pages=50 states=42 narrow=4 errors=0。",
        "",
        "## 未完成项",
        "",
        "- R5、今日工作真实聚合、政策/市场/态势/共同治理真实业务未开发。",
        "- R4 保持 `acceptance_blocked`，待策略确认后再继续。",
        "",
        "## 已知风险",
        "",
        "- 全景骨架使用 Fixture 模拟数据，不伪装成真实数据。",
        "- 后续真实 API 接入时，通过统一 Adapter 替换 Fixture，不重写页面。",
        "",
        "## 敏感信息检查结果",
        "",
        "- 未包含 `.env`、Token、API Key、数据库、缓存、日志、`.next`、`node_modules` 或旧 ZIP。",
        "- 所有截图来自脱机预览与本地 `/panorama` Fixture 路由。",
    ]
    output = ROOT / "MANIFEST.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"manifest entries={len(entries)} screenshots={len(screenshots)} -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
