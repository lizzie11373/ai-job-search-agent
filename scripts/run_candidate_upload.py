from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from job_agent.ingestion.candidate_source_upload import (
    save_uploaded_candidate_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Save one local Markdown source through the upload boundary. "
            "candidate Markdown source."
        )
    )
    parser.add_argument(
        "markdown_file",
        type=Path,
        help="Local .md file to upload into data/candidate_sources.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing file with the same name.",
    )

    args = parser.parse_args()

    source_path = args.markdown_file

    document = save_uploaded_candidate_markdown(
        filename=source_path.name,
        content=source_path.read_bytes(),
        overwrite=args.overwrite,
    )

    print("Candidate source uploaded.")
    print(f"name: {document.document_name}")
    print(f"saved_path: {document.saved_path}")
    print(f"characters: {len(document.document_text)}")


if __name__ == "__main__":
    main()
