#!/usr/bin/env python3
"""Small Tamarind REST API helper for Protein Lab skills."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable


DEFAULT_BASE_URL = "https://app.tamarind.bio/api/"
RETRYABLE_STATUS = {429, 502, 503, 504}
ALLOWED_DOWNLOAD_SCHEMES = {"http", "https"}


class TamarindError(RuntimeError):
    pass


def require_api_key() -> str:
    api_key = os.environ.get("TAMARIND_API_KEY", "").strip()
    if not api_key:
        raise TamarindError("TAMARIND_API_KEY is not set in the environment.")
    return api_key


def base_url() -> str:
    value = os.environ.get("TAMARIND_BASE_URL", DEFAULT_BASE_URL).strip()
    return value if value.endswith("/") else value + "/"


def endpoint_url(path: str, query: dict[str, Any] | None = None) -> str:
    url = urllib.parse.urljoin(base_url(), path.lstrip("/"))
    clean_query = {k: v for k, v in (query or {}).items() if v is not None}
    if clean_query:
        url += "?" + urllib.parse.urlencode(clean_query)
    return url


def decode_response(data: bytes, content_type: str = "") -> Any:
    text = data.decode("utf-8", errors="replace")
    if "json" in content_type.lower():
        return json.loads(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _build_request(
    method: str,
    path: str,
    *,
    payload: Any | None,
    query: dict[str, Any] | None,
    body: Any | None,
    content_type: str | None,
) -> urllib.request.Request:
    api_key = require_api_key()
    headers = {"x-api-key": api_key}
    request_body: Any | None = body
    if payload is not None:
        request_body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif content_type:
        headers["Content-Type"] = content_type
    return urllib.request.Request(
        endpoint_url(path, query),
        data=request_body,
        headers=headers,
        method=method.upper(),
    )


def _sleep_backoff(attempt: int) -> None:
    time.sleep(min(2 ** attempt, 30))


def api_request(
    method: str,
    path: str,
    *,
    payload: Any | None = None,
    query: dict[str, Any] | None = None,
    body: Any | None = None,
    content_type: str | None = None,
    timeout: float = 60.0,
    max_retries: int = 3,
) -> Any:
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        request = _build_request(
            method, path, payload=payload, query=query, body=body, content_type=content_type
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return decode_response(response.read(), response.headers.get("Content-Type", ""))
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            if exc.code in RETRYABLE_STATUS and attempt < max_retries:
                last_error = exc
                _sleep_backoff(attempt)
                continue
            raise TamarindError(f"HTTP {exc.code} from {path}: {body_text}") from exc
        except urllib.error.URLError as exc:
            if attempt < max_retries:
                last_error = exc
                _sleep_backoff(attempt)
                continue
            raise TamarindError(f"Request failed for {path}: {exc.reason}") from exc
    raise TamarindError(f"Request failed for {path} after retries: {last_error}")


def stream_download(url: str, out_path: Path, timeout: float = 1800.0) -> int:
    scheme = urllib.parse.urlparse(url).scheme.lower()
    if scheme not in ALLOWED_DOWNLOAD_SCHEMES:
        raise TamarindError(f"Refusing to download from unsupported URL scheme: {scheme!r}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=timeout) as response, out_path.open("wb") as handle:
        shutil.copyfileobj(response, handle, length=1024 * 1024)
    return out_path.stat().st_size


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def payload_summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"type": type(payload).__name__}
    keys = sorted(payload.keys())
    summary: dict[str, Any] = {"keys": keys}
    for label in ("jobName", "batchName", "type"):
        if label in payload:
            summary[label] = payload[label]
    settings = payload.get("settings")
    if isinstance(settings, dict):
        summary["settings_keys"] = sorted(settings.keys())
    elif isinstance(settings, list):
        summary["settings_count"] = len(settings)
    return summary


def cmd_tools(args: argparse.Namespace) -> None:
    data = api_request("GET", "tools")
    if args.tool:
        needle = args.tool.lower()
        if isinstance(data, list):
            data = [
                item
                for item in data
                if needle in str(item.get("name", "")).lower()
                or needle in str(item.get("displayName", "")).lower()
            ]
    print_json(data)


def _confirm_submission(args: argparse.Namespace, payload: Any, action: str) -> None:
    if args.confirm:
        return
    summary = {"action": action, "payload_summary": payload_summary(payload)}
    print_json({"dry_run": True, **summary})
    raise TamarindError(f"{action} requires --confirm to actually submit. Dry-run summary printed above.")


def cmd_submit_job(args: argparse.Namespace) -> None:
    payload = load_json(args.payload)
    _confirm_submission(args, payload, "submit-job")
    print_json(api_request("POST", "submit-job", payload=payload))


def cmd_submit_batch(args: argparse.Namespace) -> None:
    payload = load_json(args.payload)
    _confirm_submission(args, payload, "submit-batch")
    print_json(api_request("POST", "submit-batch", payload=payload))


def cmd_jobs(args: argparse.Namespace) -> None:
    query = {
        "jobName": args.job_name,
        "batch": args.batch,
        "batchOnly": "true" if args.batch_only else None,
        "includeSubjobs": "true" if args.include_subjobs else None,
        "organization": "true" if args.organization else None,
        "jobEmail": args.job_email,
        "limit": args.limit,
        "startKey": args.start_key,
    }
    print_json(api_request("GET", "jobs", query=query))


def normalize_presigned_url(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().strip('"')
    if isinstance(value, dict):
        for key in ("resultUrl", "url", "downloadUrl", "signedUrl"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate.strip().strip('"')
    raise TamarindError(f"Could not find result URL in response: {value!r}")


def cmd_download_result(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {"jobName": args.job_name}
    if args.file_name:
        payload["fileName"] = args.file_name
    if args.job_email:
        payload["jobEmail"] = args.job_email
    if args.pdbs_only:
        payload["pdbsOnly"] = True

    result_response = api_request("POST", "result", payload=payload)
    url = normalize_presigned_url(result_response)
    size = stream_download(url, args.out, timeout=args.download_timeout)
    print_json({"jobName": args.job_name, "out": str(args.out), "bytes": size})


def cmd_upload(args: argparse.Namespace) -> None:
    source: Path = args.path
    filename = args.filename or source.name
    query = {"folder": args.folder}
    size = source.stat().st_size

    api_key = require_api_key()
    url = endpoint_url(f"upload/{urllib.parse.quote(filename)}", query)
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/octet-stream",
        "Content-Length": str(size),
    }

    # Open as a binary file object so urllib/http.client streams via .read()
    # instead of buffering the entire payload in memory.
    with source.open("rb") as handle:
        request = urllib.request.Request(url, data=handle, method="PUT", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=args.upload_timeout) as response:
                print_json(decode_response(response.read(), response.headers.get("Content-Type", "")))
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            raise TamarindError(f"HTTP {exc.code} from upload: {body_text}") from exc
        except urllib.error.URLError as exc:
            raise TamarindError(f"Upload failed: {exc.reason}") from exc


def cmd_files(args: argparse.Namespace) -> None:
    query = {
        "includeFolders": "true" if args.include_folders else None,
        "folder": args.folder,
        "limit": args.limit,
        "offset": args.offset,
    }
    print_json(api_request("GET", "files", query=query))


def require_confirm(args: argparse.Namespace, action: str) -> None:
    if not args.confirm:
        raise TamarindError(f"{action} requires --confirm.")


def cmd_stop_job(args: argparse.Namespace) -> None:
    require_confirm(args, "stop-job")
    print_json(api_request("POST", "stop-job", payload={"jobName": args.job_name}))


def cmd_delete_job(args: argparse.Namespace) -> None:
    require_confirm(args, "delete-job")
    print_json(api_request("POST", "delete-job", payload={"jobName": args.job_name}))


def cmd_delete_file(args: argparse.Namespace) -> None:
    require_confirm(args, "delete-file")
    query = {"filePath": args.file_path, "folder": args.folder}
    print_json(api_request("DELETE", "delete-file", query=query))


def cmd_poll(args: argparse.Namespace) -> None:
    deadline = time.monotonic() + args.timeout
    last: Any = None
    consecutive_errors = 0
    while True:
        try:
            last = api_request("GET", "jobs", query={"jobName": args.job_name})
            consecutive_errors = 0
        except TamarindError as exc:
            consecutive_errors += 1
            if consecutive_errors >= args.max_errors:
                raise
            if time.monotonic() >= deadline:
                print_json({"timeout": True, "last_error": str(exc), "last": last})
                raise SystemExit(2)
            _sleep_backoff(consecutive_errors)
            continue
        status = ""
        if isinstance(last, dict):
            status = str(last.get("batchStatus") or last.get("JobStatus") or "")
        if status in {"Complete", "Stopped", "Deleted", "AggregationFailed"}:
            print_json(last)
            return
        if time.monotonic() >= deadline:
            print_json({"timeout": True, "last": last})
            raise SystemExit(2)
        time.sleep(args.interval)


def _add_submit_subparser(
    subparsers: Any,
    name: str,
    help_text: str,
    handler: Callable[[argparse.Namespace], None],
) -> None:
    parser = subparsers.add_parser(name, help=help_text)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually submit; without this flag the command prints a dry-run summary and exits non-zero.",
    )
    parser.set_defaults(func=handler)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    tools = subparsers.add_parser("tools", help="List available Tamarind tools.")
    tools.add_argument("--tool", help="Filter by tool name or display name.")
    tools.set_defaults(func=cmd_tools)

    _add_submit_subparser(subparsers, "submit-job", "Submit a single job from JSON payload.", cmd_submit_job)
    _add_submit_subparser(subparsers, "submit-batch", "Submit a batch job from JSON payload.", cmd_submit_batch)

    jobs = subparsers.add_parser("jobs", help="Query jobs.")
    jobs.add_argument("--job-name")
    jobs.add_argument("--batch")
    jobs.add_argument("--batch-only", action="store_true")
    jobs.add_argument("--include-subjobs", action="store_true")
    jobs.add_argument("--organization", action="store_true")
    jobs.add_argument("--job-email")
    jobs.add_argument("--limit", type=int)
    jobs.add_argument("--start-key")
    jobs.set_defaults(func=cmd_jobs)

    poll = subparsers.add_parser("poll", help="Poll a job until a terminal status or timeout.")
    poll.add_argument("--job-name", required=True)
    poll.add_argument("--interval", type=float, default=15.0)
    poll.add_argument("--timeout", type=float, default=3600.0)
    poll.add_argument(
        "--max-errors",
        type=int,
        default=5,
        help="Number of consecutive transport errors to tolerate before giving up.",
    )
    poll.set_defaults(func=cmd_poll)

    result = subparsers.add_parser("download-result", help="Download result zip/file for a job.")
    result.add_argument("--job-name", required=True)
    result.add_argument("--out", type=Path, required=True)
    result.add_argument("--file-name")
    result.add_argument("--job-email")
    result.add_argument("--pdbs-only", action="store_true")
    result.add_argument(
        "--download-timeout",
        type=float,
        default=1800.0,
        help="Per-request timeout for the streaming download (seconds).",
    )
    result.set_defaults(func=cmd_download_result)

    upload = subparsers.add_parser("upload", help="Upload a file to Tamarind.")
    upload.add_argument("--path", type=Path, required=True)
    upload.add_argument("--filename")
    upload.add_argument("--folder")
    upload.add_argument(
        "--upload-timeout",
        type=float,
        default=1800.0,
        help="Per-request timeout for the streaming upload (seconds).",
    )
    upload.set_defaults(func=cmd_upload)

    files = subparsers.add_parser("files", help="List uploaded files.")
    files.add_argument("--include-folders", action="store_true")
    files.add_argument("--folder")
    files.add_argument("--limit", type=int)
    files.add_argument("--offset", type=int)
    files.set_defaults(func=cmd_files)

    stop_job = subparsers.add_parser("stop-job", help="Stop a running or queued job.")
    stop_job.add_argument("--job-name", required=True)
    stop_job.add_argument("--confirm", action="store_true")
    stop_job.set_defaults(func=cmd_stop_job)

    delete_job = subparsers.add_parser("delete-job", help="Delete a job.")
    delete_job.add_argument("--job-name", required=True)
    delete_job.add_argument("--confirm", action="store_true")
    delete_job.set_defaults(func=cmd_delete_job)

    delete_file = subparsers.add_parser("delete-file", help="Delete a file or folder.")
    delete_file.add_argument("--file-path")
    delete_file.add_argument("--folder")
    delete_file.add_argument("--confirm", action="store_true")
    delete_file.set_defaults(func=cmd_delete_file)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except TamarindError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
