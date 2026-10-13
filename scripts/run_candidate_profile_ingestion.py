from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from job_agent.storage.database import (
    initialize_database,
)
from job_agent.workflows.candidate_profile_ingestion import (
    ingest_uploaded_candidate_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Upload and process one Markdown candidate source. "
            "Run again for each additional supporting material."
        )
    )
    parser.add_argument(
        "markdown_file",
        type=Path,
    )

    args = parser.parse_args()

    initialize_database()

    source_path = args.markdown_file

    result = ingest_uploaded_candidate_markdown(
        filename=source_path.name,
        content=source_path.read_bytes(),
    )

    print("Candidate source processed.")
    print(f"name: {result.document_name}")
    print(f"saved_path: {result.saved_path}")
    print(f"extracted: {result.extracted_count}")
    print(f"validated: {result.validated_count}")
    print(
        "added_evidence_ids: "
        + ", ".join(result.added_evidence_ids)
    )
    print(
        f"total_candidate_evidence: "
        f"{result.total_evidence_count}"
    )


if __name__ == "__main__":
    main()
