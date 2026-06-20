from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import prepare_pepmlm_payload as ppp  # noqa: E402


def _args(**overrides) -> argparse.Namespace:
    base = {
        "input": None,
        "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ",
        "job_name": "test_job",
        "peptide_length": 15,
        "num_designs": "8",
        "project_tag": None,
        "out": Path("/tmp/_unused.json"),
        "allow_noncanonical": False,
        "strict": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_build_payload_happy_path() -> None:
    payload, warnings = ppp.build_payload(_args())
    assert payload["jobName"] == "test_job"
    assert payload["type"] == "pepmlm"
    assert payload["settings"]["peptideLength"] == 15
    assert payload["settings"]["numDesigns"] == "8"
    assert warnings == []


def test_job_name_validation_rejects_spaces() -> None:
    with pytest.raises(ppp.PayloadError):
        ppp.build_payload(_args(job_name="bad name"))


def test_num_designs_must_be_enum() -> None:
    with pytest.raises(ppp.PayloadError):
        ppp.build_payload(_args(num_designs="5"))


def test_noncanonical_rejected_by_default() -> None:
    with pytest.raises(ppp.PayloadError) as info:
        ppp.build_payload(_args(sequence="MKTXBJOU"))
    assert "noncanonical" in str(info.value)


def test_noncanonical_allowed_with_flag() -> None:
    payload, warnings = ppp.build_payload(_args(sequence="MKTXAAAAAAAAA", allow_noncanonical=True))
    assert payload["settings"]["targetSequence"] == "MKTXAAAAAAAAA"
    assert any("noncanonical" in w for w in warnings)


def test_strict_overrides_allow() -> None:
    with pytest.raises(ppp.PayloadError):
        ppp.build_payload(_args(sequence="MKTXAAAAAAAAA", allow_noncanonical=True, strict=True))


def test_fasta_input_parses(tmp_path: Path) -> None:
    fasta = tmp_path / "target.fasta"
    fasta.write_text(">header line\nMKTAYIAK\nQRQISFVK\n")
    payload, _ = ppp.build_payload(_args(input=fasta, sequence=None))
    assert payload["settings"]["targetSequence"] == "MKTAYIAKQRQISFVK"


def test_main_writes_payload(tmp_path: Path, monkeypatch, capsys) -> None:
    out = tmp_path / "payload.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "prepare_pepmlm_payload",
            "--sequence",
            "MKTAYIAKQRQISFVKSHFSRQ",
            "--job-name",
            "demo_job",
            "--peptide-length",
            "12",
            "--num-designs",
            "4",
            "--out",
            str(out),
        ],
    )
    assert ppp.main() == 0
    assert out.is_file()
    payload = json.loads(out.read_text())
    assert payload["settings"]["peptideLength"] == 12
    capsys.readouterr()
