#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT_FALLBACK = "~/Documents/Protein Lab"


def slugify(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\bvs\.?\b", "vs", title, flags=re.IGNORECASE)
    title = re.sub(r"[^A-Za-z0-9()]+", "_", title)
    title = re.sub(r"_+", "_", title).strip("_")
    return title or "experiment_round"


def resolve_root(cli_value: str | None) -> Path:
    candidate = cli_value or os.environ.get("PROTEIN_LAB_ROOT") or DEFAULT_ROOT_FALLBACK
    return Path(candidate).expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a Protein Lab experiment round directory.")
    parser.add_argument("--title", required=True, help="Task or experiment title")
    parser.add_argument(
        "--root",
        default=None,
        help=(
            "Protein Lab root directory. Defaults to PROTEIN_LAB_ROOT env var, "
            f"then {DEFAULT_ROOT_FALLBACK}."
        ),
    )
    parser.add_argument("--slug", default=None, help="Override generated directory slug")
    args = parser.parse_args()

    root = resolve_root(args.root)
    slug = args.slug or slugify(args.title)
    round_dir = root / slug
    round_dir.mkdir(parents=True, exist_ok=True)

    plan = round_dir / f"{slug}_plan.md"
    status = round_dir / "status_log.md"

    if not plan.exists():
        plan.write_text(
            "\n".join(
                [
                    f"# {args.title}",
                    "",
                    "## 任务来源",
                    "",
                    "- 来源说明：",
                    "- 协作链接：",
                    "",
                    "## 实验目的",
                    "",
                    "## 输入与材料",
                    "",
                    "## 实验设计",
                    "",
                    "## 工具提交记录",
                    "",
                    "## 结果回来后优先看",
                    "",
                    "1. ipTM / ranking score 相对差异。",
                    "2. pLDDT 与 inter-chain PAE。",
                    "3. 5 个模型是否收敛到同一界面。",
                    "4. 对照组是否能排除非特异吸附。",
                    "",
                    "## 关键边界",
                    "",
                    "- 结构预测支持候选界面和相对排序，不单独证明机制。",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    if not status.exists():
        status.write_text(
            f"# Status Log\n\n- {datetime.now().isoformat(timespec='seconds')}: initialized `{slug}`.\n",
            encoding="utf-8",
        )

    print(round_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
