#!/usr/bin/env python3
"""Generate the panorama fixture registry from the page registry."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {
    "owner": "域主查看全景模拟工作面",
    "public": "访客查看公共世界与客户协作骨架",
    "operations": "运营者查看平台运营骨架",
    "governance": "治理者查看治理审计骨架",
    "midplatform": "架构师查看中台能力域设计视图",
    "backend": "架构师查看技术底座设计视图",
}


def main() -> int:
    registry_path = ROOT / "config" / "panorama" / "page-registry.json"
    output_path = ROOT / "config" / "panorama" / "fixture-registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    generated_at = datetime.now(timezone.utc).isoformat()
    fixtures = []
    for page in registry["pages"]:
        fixture_id = f"fixture-{page['page_id']}-normal"
        surface = page["application_surface"]
        fixtures.append({
            "fixture_id": fixture_id,
            "application_surface": surface,
            "page_id": page["page_id"],
            "realm_id": "fixture-realm-0001",
            "project_id": "fixture-project-0001",
            "user_role": "owner" if surface == "owner" else surface,
            "truth_scope": "simulation",
            "scenario": SCENARIOS.get(surface, "全景骨架模拟交互"),
            "data_mode": "fixture",
            "generated_at": generated_at,
            "source_label": "脱机设计预览 / Mock 示例数据 / 待真实接口接入",
            "simulation_marker": True,
            "no_real_write": True,
        })
    output_path.write_text(
        json.dumps({"version": registry["version"], "fixtures": fixtures}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"generated {len(fixtures)} fixtures -> {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
