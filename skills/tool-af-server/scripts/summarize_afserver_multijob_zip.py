#!/usr/bin/env python3
"""Deprecated. Use ``afserver_audit.py`` instead.

The original helper hard-coded chain "A"/"B", a 2x2 matrix fallback,
and a job-name-based offset heuristic that misbehaved on >2-chain jobs
and on naming conventions outside the GRK4/ZDHHC17 pattern. The
replacement ``afserver_audit.py`` handles arbitrary chain ids and writes
both JSON and Markdown.

This wrapper just delegates to ``afserver_audit.py`` for backwards
compatibility and prints a deprecation notice on stderr.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import afserver_audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="AlphaFold Server result zip or extracted result directory")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--out", help="Output file path; defaults to stdout")
    args = parser.parse_args()

    print(
        "warning: summarize_afserver_multijob_zip.py is deprecated; use afserver_audit.py.",
        file=sys.stderr,
    )

    summary = afserver_audit.audit(Path(args.input), persistent_extract_dir=None)
    rendered = (
        afserver_audit.render_markdown(summary)
        if args.format == "markdown"
        else __import__("json").dumps(summary, ensure_ascii=False, indent=2)
    )
    if args.out:
        Path(args.out).expanduser().write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
