from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import tamarind_api as ta  # noqa: E402


def test_require_api_key_missing(monkeypatch) -> None:
    monkeypatch.delenv("TAMARIND_API_KEY", raising=False)
    with pytest.raises(ta.TamarindError):
        ta.require_api_key()


def test_base_url_default(monkeypatch) -> None:
    monkeypatch.delenv("TAMARIND_BASE_URL", raising=False)
    assert ta.base_url() == ta.DEFAULT_BASE_URL


def test_base_url_normalizes_trailing_slash(monkeypatch) -> None:
    monkeypatch.setenv("TAMARIND_BASE_URL", "https://example.test/api")
    assert ta.base_url().endswith("/")


def test_endpoint_url_drops_none_query(monkeypatch) -> None:
    monkeypatch.setenv("TAMARIND_BASE_URL", "https://example.test/api/")
    url = ta.endpoint_url("jobs", {"jobName": "abc", "limit": None})
    assert "jobName=abc" in url
    assert "limit" not in url


def test_normalize_presigned_url_from_string() -> None:
    assert ta.normalize_presigned_url('"https://x/y"') == "https://x/y"


def test_normalize_presigned_url_from_dict() -> None:
    assert ta.normalize_presigned_url({"resultUrl": "https://x/y"}) == "https://x/y"


def test_normalize_presigned_url_missing_raises() -> None:
    with pytest.raises(ta.TamarindError):
        ta.normalize_presigned_url({})


def test_payload_summary_extracts_key_facts() -> None:
    payload = {"jobName": "abc", "type": "pepmlm", "settings": {"x": 1, "y": 2}}
    summary = ta.payload_summary(payload)
    assert summary["jobName"] == "abc"
    assert summary["type"] == "pepmlm"
    assert summary["settings_keys"] == ["x", "y"]


def test_submit_job_dry_run_blocks_without_confirm(tmp_path: Path, monkeypatch, capsys) -> None:
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps({"jobName": "abc", "type": "pepmlm", "settings": {}}))
    monkeypatch.setenv("TAMARIND_API_KEY", "fake")
    args = argparse.Namespace(payload=payload_path, confirm=False)
    with pytest.raises(ta.TamarindError) as info:
        ta.cmd_submit_job(args)
    out = capsys.readouterr().out
    assert "dry_run" in out
    assert "requires --confirm" in str(info.value)


def test_sleep_backoff_caps(monkeypatch) -> None:
    captured: list[float] = []
    monkeypatch.setattr(ta.time, "sleep", lambda secs: captured.append(secs))
    for attempt in range(7):
        ta._sleep_backoff(attempt)
    assert captured[0] == 1
    assert captured[-1] == 30  # capped
