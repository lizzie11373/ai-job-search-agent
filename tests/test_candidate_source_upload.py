from pathlib import Path

import pytest

from job_agent.ingestion.candidate_source_upload import (
    load_candidate_markdown,
    save_uploaded_candidate_markdown,
)


def test_upload_saves_markdown_and_returns_document(tmp_path: Path):
    content = (
        b"# Resume\n\n"
        b"Senior product designer with AI project experience.\n"
    )

    document = save_uploaded_candidate_markdown(
        filename="resume.md",
        content=content,
        source_dir=tmp_path,
    )

    assert document.document_name == "resume.md"
    assert document.document_text.startswith("# Resume")
    assert document.saved_path == tmp_path / "resume.md"
    assert document.saved_path.read_bytes() == content


def test_upload_supports_markdown_only(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match=r"Markdown \(\.md\) only",
    ):
        save_uploaded_candidate_markdown(
            filename="resume.txt",
            content=b"plain text",
            source_dir=tmp_path,
        )


def test_upload_rejects_empty_or_invalid_utf8(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="empty",
    ):
        save_uploaded_candidate_markdown(
            filename="empty.md",
            content=b"",
            source_dir=tmp_path,
        )

    with pytest.raises(
        ValueError,
        match="UTF-8",
    ):
        save_uploaded_candidate_markdown(
            filename="bad.md",
            content=b"\xff\xfe",
            source_dir=tmp_path,
        )


def test_upload_discards_path_components_and_does_not_overwrite_by_default(
    tmp_path: Path,
):
    first = save_uploaded_candidate_markdown(
        filename="../../resume.md",
        content=b"# Resume\n",
        source_dir=tmp_path,
    )

    assert first.document_name == "resume.md"
    assert first.saved_path == tmp_path / "resume.md"

    with pytest.raises(FileExistsError):
        save_uploaded_candidate_markdown(
            filename="resume.md",
            content=b"# New Resume\n",
            source_dir=tmp_path,
        )


def test_load_saved_markdown(tmp_path: Path):
    source_path = tmp_path / "project.md"
    source_path.write_text(
        "# Project\n\nBuilt a RAG assistant.\n",
        encoding="utf-8",
    )

    document = load_candidate_markdown(
        source_path
    )

    assert document.document_name == "project.md"
    assert "Built a RAG assistant." in document.document_text
    assert document.saved_path == source_path
