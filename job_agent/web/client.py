from html.parser import HTMLParser
import json
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from job_agent.web.models import (
    JobPostingMetadata,
    PageSnapshot,
)


DEFAULT_TIMEOUT_SECONDS = 12
MAX_RESPONSE_BYTES = 2_000_000


class _VisibleTextParser(HTMLParser):
    """
    Deterministic HTML parser.

    It extracts:
    - <title>
    - visible text outside script/style/noscript/svg
    - raw application/ld+json blocks

    JSON-LD matters because many job pages publish structured
    JobPosting fields such as title, hiringOrganization, jobLocation,
    and identifier. Those signals are much safer for deterministic
    identity checks than searching arbitrary visible page text.
    """

    SKIPPED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
    }

    def __init__(self) -> None:
        super().__init__()

        self._skip_depth = 0
        self._inside_title = False

        self._inside_json_ld = False
        self._current_json_ld_parts: list[str] = []

        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self._json_ld_blocks: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        tag = tag.lower()

        if tag == "script":
            attrs_dict = {
                str(key).lower(): value
                for key, value in attrs
            }

            script_type = (
                attrs_dict.get("type")
                or ""
            ).lower()

            if script_type == "application/ld+json":
                self._inside_json_ld = True
                self._current_json_ld_parts = []

        if tag in self.SKIPPED_TAGS:
            self._skip_depth += 1

        if tag == "title":
            self._inside_title = True

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = tag.lower()

        if tag == "title":
            self._inside_title = False

        if (
            tag == "script"
            and self._inside_json_ld
        ):
            block = "".join(
                self._current_json_ld_parts
            ).strip()

            if block:
                self._json_ld_blocks.append(
                    block
                )

            self._inside_json_ld = False
            self._current_json_ld_parts = []

        if (
            tag in self.SKIPPED_TAGS
            and self._skip_depth > 0
        ):
            self._skip_depth -= 1

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self._inside_json_ld:
            self._current_json_ld_parts.append(
                data
            )

        cleaned = " ".join(
            data.split()
        )

        if not cleaned:
            return

        if self._inside_title:
            self._title_parts.append(
                cleaned
            )

        if self._skip_depth == 0:
            self._text_parts.append(
                cleaned
            )

    @property
    def title(self) -> str | None:
        if not self._title_parts:
            return None

        title = " ".join(
            self._title_parts
        ).strip()

        return title or None

    @property
    def text(self) -> str:
        text = " ".join(
            self._text_parts
        )

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    @property
    def json_ld_blocks(self) -> tuple[str, ...]:
        return tuple(
            self._json_ld_blocks
        )


def _as_list(value) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _json_ld_types(
    node: dict,
) -> set[str]:
    raw_type = node.get("@type")

    if raw_type is None:
        return set()

    return {
        str(value).lower()
        for value in _as_list(raw_type)
    }


def _walk_json_nodes(value):
    if isinstance(value, dict):
        yield value

        for child in value.values():
            yield from _walk_json_nodes(
                child
            )

    elif isinstance(value, list):
        for child in value:
            yield from _walk_json_nodes(
                child
            )


def _clean_string(value) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        cleaned = " ".join(
            value.split()
        ).strip()

        return cleaned or None

    return None


def _extract_company(
    node: dict,
) -> str | None:
    organization = node.get(
        "hiringOrganization"
    )

    if isinstance(
        organization,
        str,
    ):
        return _clean_string(
            organization
        )

    if isinstance(
        organization,
        dict,
    ):
        return _clean_string(
            organization.get("name")
        )

    return None


def _extract_country(
    value,
) -> str | None:
    if isinstance(value, str):
        return _clean_string(value)

    if isinstance(value, dict):
        return (
            _clean_string(
                value.get("name")
            )
            or _clean_string(
                value.get("@id")
            )
        )

    return None


def _format_location(
    value,
) -> str | None:
    if isinstance(value, str):
        return _clean_string(value)

    if not isinstance(value, dict):
        return None

    address = value.get("address")

    if isinstance(address, str):
        return _clean_string(address)

    if not isinstance(address, dict):
        address = value

    parts = [
        _clean_string(
            address.get("addressLocality")
        ),
        _clean_string(
            address.get("addressRegion")
        ),
        _extract_country(
            address.get("addressCountry")
        ),
    ]

    parts = [
        part
        for part in parts
        if part
    ]

    if parts:
        return ", ".join(parts)

    return (
        _clean_string(
            value.get("name")
        )
        or _clean_string(
            address.get("name")
        )
    )


def _extract_locations(
    value,
) -> tuple[str, ...]:
    locations: list[str] = []

    for item in _as_list(value):
        location = _format_location(
            item
        )

        if (
            location
            and location not in locations
        ):
            locations.append(
                location
            )

    return tuple(locations)


def _extract_identifier(
    value,
) -> str | None:
    if isinstance(value, str):
        return _clean_string(value)

    if isinstance(value, dict):
        return (
            _clean_string(
                value.get("value")
            )
            or _clean_string(
                value.get("name")
            )
        )

    for item in _as_list(value):
        identifier = _extract_identifier(
            item
        )

        if identifier:
            return identifier

    return None


def _parse_job_posting_metadata(
    json_ld_blocks: tuple[str, ...],
) -> tuple[JobPostingMetadata, ...]:
    """
    Parse only schema.org JobPosting objects from JSON-LD.

    Invalid JSON-LD blocks are ignored rather than turning page
    retrieval into a technical failure. A page may contain unrelated
    or malformed structured-data scripts while its HTML remains usable.
    """

    postings: list[
        JobPostingMetadata
    ] = []

    for block in json_ld_blocks:
        try:
            parsed = json.loads(
                block
            )

        except json.JSONDecodeError:
            continue

        for node in _walk_json_nodes(
            parsed
        ):
            if (
                "jobposting"
                not in _json_ld_types(
                    node
                )
            ):
                continue

            posting = JobPostingMetadata(
                title=_clean_string(
                    node.get("title")
                ),
                company=_extract_company(
                    node
                ),
                locations=_extract_locations(
                    node.get("jobLocation")
                ),
                applicant_locations=(
                    _extract_locations(
                        node.get(
                            "applicantLocationRequirements"
                        )
                    )
                ),
                job_location_type=(
                    _clean_string(
                        node.get(
                            "jobLocationType"
                        )
                    )
                ),
                identifier=(
                    _extract_identifier(
                        node.get("identifier")
                    )
                ),
            )

            if posting not in postings:
                postings.append(
                    posting
                )

    return tuple(postings)


def fetch_web_page(
    url: str,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> PageSnapshot:
    """
    Fetch one page with deterministic HTTP.

    Cost policy:
        Try ordinary HTTP before paying for another model/tool call.

    Important boundary:
        This function does NOT decide VERIFIED / UNVERIFIED.
        It only retrieves page data.

    HTTP statuses such as 404 or 403 are returned as retrieval
    outcomes instead of being converted into business states.
    Network-level failures other than HTTP responses intentionally
    bubble upward as technical failures.
    """

    url = url.strip()

    if not url:
        raise ValueError(
            "URL cannot be empty."
        )

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; AIJobSearchAgent/1.0)"
            ),
            "Accept": (
                "text/html,application/xhtml+xml"
            ),
        },
    )

    try:
        response = urlopen(
            request,
            timeout=timeout_seconds,
        )

    except HTTPError as error:
        content_type = (
            error.headers.get_content_type()
            if error.headers
            else None
        )

        return PageSnapshot(
            requested_url=url,
            final_url=(
                error.geturl()
                or url
            ),
            status_code=error.code,
            content_type=content_type,
            title=None,
            text="",
        )

    with response:
        status_code = (
            getattr(
                response,
                "status",
                200,
            )
        )

        final_url = response.geturl()

        content_type = (
            response.headers.get_content_type()
            if response.headers
            else None
        )

        raw = response.read(
            MAX_RESPONSE_BYTES
        )

        charset = (
            response.headers.get_content_charset()
            if response.headers
            else None
        ) or "utf-8"

    if (
        content_type
        and content_type
        not in {
            "text/html",
            "application/xhtml+xml",
        }
    ):
        return PageSnapshot(
            requested_url=url,
            final_url=final_url,
            status_code=status_code,
            content_type=content_type,
            title=None,
            text="",
        )

    html = raw.decode(
        charset,
        errors="replace",
    )

    parser = _VisibleTextParser()
    parser.feed(html)

    job_postings = (
        _parse_job_posting_metadata(
            parser.json_ld_blocks
        )
    )

    return PageSnapshot(
        requested_url=url,
        final_url=final_url,
        status_code=status_code,
        content_type=content_type,
        title=parser.title,
        text=parser.text,
        job_postings=job_postings,
    )
