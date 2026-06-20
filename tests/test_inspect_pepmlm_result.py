from __future__ import annotations

import json
import zipfile
from pathlib import Path

import inspect_pepmlm_result as ipr  # noqa: E402


def _make_zip(tmp_path: Path, files: dict[str, str]) -> Path:
    zip_path = tmp_path / "raw.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, body in files.items():
            zf.writestr(name, body)
    return zip_path


def test_csv_without_candidate_column_is_not_regex_mined(tmp_path: Path) -> None:
    csv_body = (
        "id,target,score\n"
        "1,MKTAYIAKQRQISFVKSHFSRQ,0.42\n"
        "2,MKTAYIAKQRQISFVKSHFSRQ,0.30\n"
    )
    zip_path = _make_zip(tmp_path, {"results.csv": csv_body})
    inventory, text_files = ipr.iter_package_files(zip_path)
    rows = ipr.dedupe_candidates(ipr.parse_candidates(text_files, expected_length=15), 15)
    assert inventory[0]["path"] == "results.csv"
    assert rows == []


def test_csv_with_candidate_column_parses(tmp_path: Path) -> None:
    csv_body = "rank,peptide,score\n1,ACDEFGHIKLMNPQR,0.91\n2,ACDEFGHIKLMNPQR,0.85\n3,VWYACDEFGHIKLMN,0.80\n"
    zip_path = _make_zip(tmp_path, {"candidates.csv": csv_body})
    _, text_files = ipr.iter_package_files(zip_path)
    rows = ipr.dedupe_candidates(ipr.parse_candidates(text_files, expected_length=15), 15)
    assert {row["sequence"] for row in rows} == {"ACDEFGHIKLMNPQR", "VWYACDEFGHIKLMN"}
    duplicated = next(row for row in rows if row["sequence"] == "ACDEFGHIKLMNPQR")
    assert duplicated["duplicate_count"] == 2


def test_jsonl_input_extracts_candidates(tmp_path: Path) -> None:
    lines = [
        json.dumps({"rank": 1, "peptide": "MKTAYIAKQRQISFV", "score": 0.7}),
        json.dumps({"rank": 2, "peptide": "ACDEFGHIKLMNPQR", "score": 0.5}),
    ]
    zip_path = _make_zip(tmp_path, {"out.jsonl": "\n".join(lines)})
    _, text_files = ipr.iter_package_files(zip_path)
    rows = ipr.dedupe_candidates(ipr.parse_candidates(text_files, expected_length=15), 15)
    assert {row["sequence"] for row in rows} == {"MKTAYIAKQRQISFV", "ACDEFGHIKLMNPQR"}


def test_oversize_text_marked_in_inventory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ipr, "TEXT_SIZE_LIMIT_BYTES", 32)
    long_body = "x" * 64
    zip_path = _make_zip(tmp_path, {"huge.csv": long_body, "small.csv": "peptide\nACDEFGHIK\n"})
    inventory, text_files = ipr.iter_package_files(zip_path)
    huge_entry = next(entry for entry in inventory if entry["path"] == "huge.csv")
    assert huge_entry["kind"] == "text-too-large"
    assert all(tf.path != "huge.csv" for tf in text_files)


def test_issue_flags_detect_noncanonical_and_homopolymer() -> None:
    flags = ipr.issue_flags("AAAAAACCCXBJ", expected_length=12)
    assert "noncanonical-aa" in flags
    assert "homopolymer-run" in flags
    assert "high-cysteine" in flags
