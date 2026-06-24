from __future__ import annotations

from pathlib import Path

import pytest

import knowledge_base as kb  # noqa: E402


def test_init_wiki_creates_standard_structure(tmp_path: Path) -> None:
    written = kb.init_wiki(tmp_path)
    assert (tmp_path / "index.md").is_file()
    for dirname in kb.WIKI_DIRS:
        assert (tmp_path / dirname / "index.md").is_file()
    assert written


def test_index_wiki_lists_markdown_files(tmp_path: Path) -> None:
    kb.init_wiki(tmp_path)
    data = kb.index_wiki(tmp_path)
    assert data["file_count"] >= len(kb.WIKI_DIRS) + 1
    assert any(row["path"] == "projects/index.md" for row in data["files"])


def test_write_note_rejects_secret_like_text(tmp_path: Path) -> None:
    kb.init_wiki(tmp_path)
    with pytest.raises(ValueError):
        kb.write_note(tmp_path, "guardrails", "Bad Note", "Do not save api key abc")


def test_write_note_creates_category_note(tmp_path: Path) -> None:
    kb.init_wiki(tmp_path)
    path = kb.write_note(tmp_path, "decisions", "Use Local Wiki", "Decision body.")
    assert path.relative_to(tmp_path).as_posix() == "decisions/use-local-wiki.md"
    assert "Decision body." in path.read_text()


def test_assert_no_secret_text_allows_word_neighbours() -> None:
    # These previously tripped the substring guard; word boundaries should let them through.
    kb.assert_no_secret_text("Tokenizer notes for HuggingFace BPE.")  # substring 'token'
    kb.assert_no_secret_text("Secrets management is out of scope.")    # 'secret' inside 'secrets'
    kb.assert_no_secret_text("Cookbook chapter on auth design.")       # 'cook' near 'cookie'


def test_assert_no_secret_text_rejects_high_entropy_hex() -> None:
    fake_hex = "deadbeef" * 6  # 48 hex chars looks like a hashed credential
    with pytest.raises(ValueError):
        kb.assert_no_secret_text(f"deploy key = {fake_hex}")
