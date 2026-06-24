#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


WIKI_DIRS = ["projects", "experiments", "tools", "protocols", "decisions", "literature", "guardrails"]
# Word-bounded patterns so legitimate notes mentioning "tokenizer",
# "password-less auth", "HTTP cookie", or "secret sauce" are not rejected.
# This is a soft hint guard, not a real secret detector.
SECRET_PATTERNS = (
    r"\bapi[\s_-]*key\b",
    r"\btoken\b",
    r"\bpassword\b",
    r"\bsecret\b",
    r"\bcookie\b",
)
HEX_RUN_RE = re.compile(r"\b[A-Fa-f0-9]{40,}\b")
BASE64_RUN_RE = re.compile(r"\b[A-Za-z0-9+]{40,}={0,2}\b")


def slugify(title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title.strip().lower())
    return re.sub(r"-+", "-", slug).strip("-") or "note"


def looks_like_high_entropy_secret(text: str) -> bool:
    """Heuristic: hex runs >=40 chars, or base64-shaped runs that contain at
    least one lowercase letter or digit. The lowercase/digit gate prevents
    long all-uppercase amino-acid sequences from being mistaken for a token.
    """
    if HEX_RUN_RE.search(text):
        return True
    for match in BASE64_RUN_RE.finditer(text):
        token = match.group(0)
        if any(c.islower() or c.isdigit() for c in token):
            return True
    return False


def assert_no_secret_text(text: str) -> None:
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in SECRET_PATTERNS):
        raise ValueError("Refusing to write text containing secret-like words.")
    if looks_like_high_entropy_secret(text):
        raise ValueError("Refusing to write text containing a high-entropy token-like string.")


def init_wiki(root: Path) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for dirname in WIKI_DIRS:
        folder = root / dirname
        folder.mkdir(exist_ok=True)
        index = folder / "index.md"
        if not index.exists():
            index.write_text(f"# {dirname.title()}\n\n", encoding="utf-8")
            written.append(index)
    top_index = root / "index.md"
    if not top_index.exists():
        lines = ["# Protein Lab Knowledge Base", "", "## Sections", ""]
        lines.extend([f"- [{name}]({name}/index.md)" for name in WIKI_DIRS])
        lines.append("")
        top_index.write_text("\n".join(lines), encoding="utf-8")
        written.append(top_index)
    return written


def index_wiki(root: Path) -> dict[str, Any]:
    files = []
    if root.exists():
        for path in sorted(root.rglob("*.md")):
            if any(part.startswith(".") for part in path.relative_to(root).parts):
                continue
            first_line = ""
            try:
                first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
            except IndexError:
                first_line = ""
            files.append(
                {
                    "path": str(path.relative_to(root)),
                    "title": first_line.lstrip("# ").strip() or path.stem,
                    "bytes": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                }
            )
    return {
        "root": str(root),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "file_count": len(files),
        "files": files,
    }


def write_note(root: Path, category: str, title: str, body: str) -> Path:
    if category not in WIKI_DIRS:
        raise ValueError(f"category must be one of: {', '.join(WIKI_DIRS)}")
    assert_no_secret_text(body)
    folder = root / category
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{slugify(title)}.md"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(f"# {title}\n\n{body.rstrip()}\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Protein Lab local Markdown knowledge-base helper.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--root", required=True)
    index = sub.add_parser("index")
    index.add_argument("--root", required=True)
    index.add_argument("--out", default=None)
    note = sub.add_parser("write-note")
    note.add_argument("--root", required=True)
    note.add_argument("--category", choices=WIKI_DIRS, required=True)
    note.add_argument("--title", required=True)
    note.add_argument("--body", required=True)
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if args.command == "init":
        written = init_wiki(root)
        print(json.dumps({"root": str(root), "written": [str(p) for p in written]}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "index":
        data = index_wiki(root)
        text = json.dumps(data, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).expanduser().write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    if args.command == "write-note":
        path = write_note(root, args.category, args.title, args.body)
        print(path)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
