from __future__ import annotations

import json
import zipfile
from pathlib import Path

import afserver_audit as af  # noqa: E402


def _two_chain_full(num_tokens_a: int = 3, num_tokens_b: int = 3) -> dict[str, object]:
    total = num_tokens_a + num_tokens_b
    token_chain_ids = ["A"] * num_tokens_a + ["B"] * num_tokens_b
    token_res_ids = list(range(1, num_tokens_a + 1)) + list(range(1, num_tokens_b + 1))
    pae = [[1.0 if i != j else 0.0 for j in range(total)] for i in range(total)]
    contact = [[0.9 if i != j else 0.0 for j in range(total)] for i in range(total)]
    atom_chain_ids = ["A"] * num_tokens_a + ["B"] * num_tokens_b
    atom_plddts = [80.0] * num_tokens_a + [70.0] * num_tokens_b
    return {
        "token_chain_ids": token_chain_ids,
        "token_res_ids": token_res_ids,
        "pae": pae,
        "contact_probs": contact,
        "atom_chain_ids": atom_chain_ids,
        "atom_plddts": atom_plddts,
    }


def _make_af_zip(tmp_path: Path) -> Path:
    job_dir = "demo_job"
    files = {
        f"{job_dir}/job_request.json": json.dumps([{"name": "demo_job", "modelSeeds": [42]}]),
        f"{job_dir}/demo_summary_confidences_0.json": json.dumps(
            {"ranking_score": 0.8, "iptm": 0.7, "ptm": 0.6, "chain_pair_iptm": [[1.0, 0.5], [0.5, 1.0]]}
        ),
        f"{job_dir}/demo_full_data_0.json": json.dumps(_two_chain_full()),
        f"{job_dir}/demo_summary_confidences_1.json": json.dumps({"ranking_score": 0.9, "iptm": 0.8, "ptm": 0.7}),
        f"{job_dir}/demo_full_data_1.json": json.dumps(_two_chain_full()),
    }
    zip_path = tmp_path / "af.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, body in files.items():
            zf.writestr(name, body)
    return zip_path


def test_audit_with_out_dir_keeps_extraction(tmp_path: Path) -> None:
    zip_path = _make_af_zip(tmp_path)
    out_dir = tmp_path / "out"
    extract_dir = out_dir / "_extracted"
    summary = af.audit(zip_path, persistent_extract_dir=extract_dir)
    assert summary["job_count"] == 1
    job = summary["jobs"][0]
    assert job["job_name"] == "demo_job"
    assert job["model_count"] == 2
    # Relative paths should be resolvable against result_root post-call.
    result_root = Path(summary["result_root"])
    for model in job["models"]:
        assert (result_root / model["summary_path"]).is_file()
        assert (result_root / model["full_data_path"]).is_file()
    # Best model picks the higher ranking_score.
    assert job["best_model"]["ranking_score"] == 0.9


def test_audit_without_out_dir_uses_temp(tmp_path: Path) -> None:
    zip_path = _make_af_zip(tmp_path)
    summary = af.audit(zip_path, persistent_extract_dir=None)
    assert summary["paths_relative_to"] == "result_root"
    # result_root is a temp dir that is cleaned up after audit returns, so
    # we only verify that the relative paths are sensible strings.
    job = summary["jobs"][0]
    for model in job["models"]:
        assert model["summary_path"].endswith(".json")


def test_render_markdown_runs(tmp_path: Path) -> None:
    zip_path = _make_af_zip(tmp_path)
    summary = af.audit(zip_path, persistent_extract_dir=None)
    text = af.render_markdown(summary)
    assert "demo_job" in text
    assert "Job Summary" in text


def test_directory_input_uses_relative_paths(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "demo_job").mkdir(parents=True)
    (src / "demo_job" / "job_request.json").write_text(json.dumps([{"name": "demo_job", "modelSeeds": [1]}]))
    (src / "demo_job" / "demo_summary_confidences_0.json").write_text(
        json.dumps({"ranking_score": 0.5, "iptm": 0.4, "ptm": 0.3})
    )
    (src / "demo_job" / "demo_full_data_0.json").write_text(json.dumps(_two_chain_full()))

    summary = af.audit(src, persistent_extract_dir=None)
    assert summary["result_root"] == str(src.resolve())
    model = summary["jobs"][0]["models"][0]
    assert (Path(summary["result_root"]) / model["summary_path"]).is_file()
