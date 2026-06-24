#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Any


TOOL_HINTS = ("api", "cli", "web", "browser", "gpu", "modal", "tamarind", "alphafold", "server", "平台", "工具")
WIKI_HINTS = ("result", "experiment", "literature", "paper", "decision", "项目", "实验结果", "文献", "结论", "背景")
SKILL_HINTS = ("workflow", "repeat", "procedure", "guardrail", "流程", "反复", "规范", "护栏")


def classify(text: str, *, repeatable: bool = False, team_specific: bool = False) -> dict[str, Any]:
    lowered = text.lower()
    has_tool = any(hint in lowered for hint in TOOL_HINTS)
    has_wiki = any(hint in lowered for hint in WIKI_HINTS)
    has_skill = repeatable or any(hint in lowered for hint in SKILL_HINTS)
    if has_tool and has_skill:
        primary = "tool-creator"
        reason = "repeatable third-party tool operation should become a tool-* skill"
    elif has_wiki and not has_skill:
        primary = "knowledge-base"
        reason = "project fact, result, literature, or decision belongs in wiki"
    elif has_skill and team_specific:
        primary = "team-research-skill"
        reason = "repeatable but team-specific workflow should not be bundled as plugin core by default"
    elif has_skill:
        primary = "plugin-core-skill"
        reason = "stable repeatable workflow can be encoded as a reusable skill"
    else:
        primary = "knowledge-base"
        reason = "default to wiki until repeatability is proven"
    also = []
    if has_wiki and primary != "knowledge-base":
        also.append("knowledge-base")
    return {
        "primary": primary,
        "also_update": also,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a Protein Lab lesson/capability destination.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--repeatable", action="store_true")
    parser.add_argument("--team-specific", action="store_true")
    args = parser.parse_args()
    print(json.dumps(classify(args.text, repeatable=args.repeatable, team_specific=args.team_specific), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
