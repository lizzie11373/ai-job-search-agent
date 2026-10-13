from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_CANDIDATE_SOURCE_DIR = Path(
    "data/candidate_sources"
)

SUPPORTED_SUFFIX = ".md"


@dataclass(frozen=True)
class CandidateSourceDocument:
    """
    One user-provided candidate background source.

    This object is deliberately small. The downstream evidence pipeline
    already accepts:

        document_name
        document_text

    so the upload layer only needs to turn an uploaded Markdown file into
    those two values and keep a durable local copy.
    """

    document_name: str
    document_text: str
    saved_path: Path


def _validate_markdown_filename(
    filename: str,
) -> str:
    """
    Validate and normalize one uploaded filename.

    Path components supplied by a browser/client are discarded so an
    uploaded name cannot escape the candidate-source directory.
    """

    safe_name = Path(filename).name.strip()

    if not safe_name:
        raise ValueError(
            "Uploaded candidate source must have a filename."
        )

    if Path(safe_name).suffix.lower() != SUPPORTED_SUFFIX:
        raise ValueError(
            "Candidate source upload supports Markdown (.md) only."
        )

    return safe_name


def _decode_markdown(
    content: bytes,
) -> str:
    """
    Decode one uploaded Markdown file as UTF-8 text.
    """

    if not content:
        raise ValueError(
            "Uploaded candidate source is empty."
        )

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Candidate source must be UTF-8 encoded Markdown."
        ) from exc

    if not text.strip():
        raise ValueError(
            "Uploaded candidate source contains no usable text."
        )

    return text


def save_uploaded_candidate_markdown(
    *,
    filename: str,
    content: bytes,
    source_dir: str | Path = DEFAULT_CANDIDATE_SOURCE_DIR,
    overwrite: bool = False,
) -> CandidateSourceDocument:
    """
    Save one uploaded Markdown source and return its text representation.

    This function is UI-framework neutral. A future Streamlit/Flask/FastAPI
    upload handler only needs to pass:

        uploaded filename
        uploaded bytes

    The file is saved under data/candidate_sources by default and the
    returned document can be passed directly into the existing evidence
    extraction pipeline.

    By default an existing file with the same name is not overwritten.
    """

    safe_name = _validate_markdown_filename(
        filename
    )
    document_text = _decode_markdown(
        content
    )

    source_dir = Path(source_dir)
    source_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_path = source_dir / safe_name

    if saved_path.exists() and not overwrite:
        raise FileExistsError(
            f"Candidate source already exists: {safe_name}"
        )

    # Write the exact uploaded bytes so the durable source remains the
    # source of truth for later evidence grounding.
    saved_path.write_bytes(content)

    return CandidateSourceDocument(
        document_name=safe_name,
        document_text=document_text,
        saved_path=saved_path,
    )


def load_candidate_markdown(
    path: str | Path,
) -> CandidateSourceDocument:
    """
    Load one already-saved Markdown source from disk.

    This is useful for local development and for reusing documents that
    were uploaded during an earlier session.
    """

    path = Path(path)

    safe_name = _validate_markdown_filename(
        path.name
    )

    if not path.is_file():
        raise FileNotFoundError(
            f"Candidate source does not exist: {path}"
        )

    content = path.read_bytes()
    document_text = _decode_markdown(
        content
    )

    return CandidateSourceDocument(
        document_name=safe_name,
        document_text=document_text,
        saved_path=path,
    )
