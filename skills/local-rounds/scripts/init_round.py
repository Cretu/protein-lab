#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT_FALLBACK = "~/Documents/Protein Lab"
DEFAULT_CONFIG_PATH = "~/.config/protein-lab/config.json"
PROJECT_CONFIG_DIR = ".protein-lab"
PROJECT_CONFIG_FILE = "project.json"


def slugify(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\bvs\.?\b", "vs", title, flags=re.IGNORECASE)
    title = re.sub(r"[^A-Za-z0-9()]+", "_", title)
    title = re.sub(r"_+", "_", title).strip("_")
    return title or "experiment_round"


def find_project_config(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        path = candidate / PROJECT_CONFIG_DIR / PROJECT_CONFIG_FILE
        if path.exists():
            return path
    return None


def read_config_root(config_path: str | None = None, *, cwd: Path | None = None) -> str | None:
    project_config = find_project_config(cwd)
    if project_config:
        path = project_config
    else:
        path = Path(config_path or DEFAULT_CONFIG_PATH).expanduser()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    root = data.get("workspace_root")
    return root if isinstance(root, str) and root.strip() else None


def resolve_root(
    cli_value: str | None,
    *,
    use_cwd: bool = True,
    config_path: str | None = None,
    cwd: Path | None = None,
) -> Path:
    current = cwd or Path.cwd()
    if cli_value:
        candidate = cli_value
    elif use_cwd:
        candidate = read_config_root(config_path, cwd=current) or str(current)
    else:
        candidate = read_config_root(config_path, cwd=current) or os.environ.get("PROTEIN_LAB_ROOT") or DEFAULT_ROOT_FALLBACK
    return Path(candidate).expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a Protein Lab experiment round directory.")
    parser.add_argument("--title", required=True, help="Task or experiment title")
    parser.add_argument(
        "--root",
        default=None,
        help=(
            "Protein Lab workspace root. Overrides current directory, config, env var, "
            f"and fallback {DEFAULT_ROOT_FALLBACK}."
        ),
    )
    parser.add_argument(
        "--no-cwd",
        action="store_true",
        help=(
            "Do not use the current directory as the workspace. Resolution then uses "
            f"{DEFAULT_CONFIG_PATH}, PROTEIN_LAB_ROOT, then {DEFAULT_ROOT_FALLBACK}."
        ),
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Protein Lab local config path")
    parser.add_argument("--slug", default=None, help="Override generated directory slug")
    args = parser.parse_args()

    root = resolve_root(args.root, use_cwd=not args.no_cwd, config_path=args.config)
    slug = args.slug or slugify(args.title)
    round_dir = root / slug
    round_dir.mkdir(parents=True, exist_ok=True)
    for child in ("inputs", "outputs/raw", "outputs/parsed", "reports"):
        (round_dir / child).mkdir(parents=True, exist_ok=True)

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
                    "- 输入文件：`inputs/`",
                    "",
                    "## 实验设计",
                    "",
                    "## 工具提交记录",
                    "",
                    "- 原始输出：`outputs/raw/`",
                    "- 解析产物：`outputs/parsed/`",
                    "- 报告：`reports/`",
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
