from types import SimpleNamespace
from urllib.error import URLError

import job_agent.agents.job_resolution as resolution_module
from job_agent.agents.job_relevance_evaluator import JobPageEvaluation
from job_agent.models.job_candidate import (
    JobCandidate,
    JobResolutionReason,
    JobVerificationResult,
)
from job_agent.search.models import SearchResult
from job_agent.web.models import PageSnapshot


LONG_TEXT = (
    "Role overview responsibilities qualifications skills experience benefits "
    "application details team collaboration requirements. " * 25
)


def make_page(url: str, title: str = "Job Posting") -> PageSnapshot:
    return PageSnapshot(
        requested_url=url,
        final_url=url,
        status_code=200,
        content_type="text/html",
        title=title,
        text=LONG_TEXT,
    )


def one_match(job_candidate, pages):
    return [
        JobPageEvaluation(
            page=page,
            is_match=(i == 0),
            sufficiently_complete=(i == 0),
            reason="mock",
        )
        for i, page in enumerate(pages)
    ]


def no_match(job_candidate, pages):
    return [
        JobPageEvaluation(
            page=page,
            is_match=False,
            sufficiently_complete=True,
            reason="mock no match",
        )
        for page in pages
    ]


def test_linkedin_skips_source_url_and_searches(monkeypatch):
    candidate = JobCandidate(
        source="LINKEDIN",
        source_message_id="email-1",
        title="Intermediate Architect",
        company="S9 Architecture",
        location="New York",
        source_url="https://www.linkedin.com/jobs/view/123",
    )

    target = "https://app.trinethire.com/companies/s9/jobs/123"
    calls = {"search": 0, "source_fetch": 0}

    def fake_search(query):
        calls["search"] += 1
        assert "careers" not in query.lower()
        return SimpleNamespace(results=[SearchResult(url=target)])

    def fake_fetch(url):
        if "linkedin.com" in url:
            calls["source_fetch"] += 1
            raise AssertionError("LinkedIn source_url must not be fetched")
        return make_page(url)

    monkeypatch.setattr(resolution_module, "search_web", fake_search)
    monkeypatch.setattr(resolution_module, "fetch_web_page", fake_fetch)
    monkeypatch.setattr(resolution_module, "evaluate_job_pages", one_match)

    resolved = resolution_module.resolve_job_candidate(candidate)

    assert len(resolved) == 1
    assert resolved[0].canonical_job_url == target
    assert calls == {"search": 1, "source_fetch": 0}
    assert candidate.verification_result == JobVerificationResult.VERIFIED


def test_other_source_direct_url_success_avoids_search(monkeypatch):
    candidate = JobCandidate(
        source="COMPANY_ALERT",
        source_message_id="email-2",
        title="AI Product Manager",
        company="Example AI",
        location="San Francisco",
        source_url="https://careers.example.ai/jobs/123",
    )

    calls = {"search": 0, "fetch": 0}

    def fake_fetch(url):
        calls["fetch"] += 1
        return make_page(url)

    def fake_search(query):
        calls["search"] += 1
        raise AssertionError("Search should not run when direct URL succeeds")

    monkeypatch.setattr(resolution_module, "fetch_web_page", fake_fetch)
    monkeypatch.setattr(resolution_module, "search_web", fake_search)
    monkeypatch.setattr(resolution_module, "evaluate_job_pages", one_match)

    resolved = resolution_module.resolve_job_candidate(candidate)

    assert len(resolved) == 1
    assert calls == {"search": 0, "fetch": 1}


def test_other_source_direct_failure_immediately_falls_back(monkeypatch):
    candidate = JobCandidate(
        source="OTHER_ALERT",
        source_message_id="email-3",
        title="AI Product Manager",
        company="Example AI",
        location="San Francisco",
        source_url="https://blocked.example/job/123",
    )

    target = "https://jobs.example.com/ai-product-manager"
    calls = {"search": 0, "direct": 0}

    def fake_fetch(url):
        if "blocked.example" in url:
            calls["direct"] += 1
            raise URLError("blocked")
        return make_page(url)

    def fake_search(query):
        calls["search"] += 1
        return SimpleNamespace(results=[SearchResult(url=target)])

    monkeypatch.setattr(resolution_module, "fetch_web_page", fake_fetch)
    monkeypatch.setattr(resolution_module, "search_web", fake_search)
    monkeypatch.setattr(resolution_module, "evaluate_job_pages", one_match)

    resolved = resolution_module.resolve_job_candidate(candidate)

    assert len(resolved) == 1
    assert calls == {"search": 1, "direct": 1}


def test_fetches_in_batches_and_stops_after_second_batch(monkeypatch):
    candidate = JobCandidate(
        source="INDEED",
        source_message_id="email-4",
        title="Product Manager",
        company="Example AI",
        location="New York",
        source_url="https://indeed.com/viewjob?jk=ignored",
    )

    urls = [f"https://jobs.example.com/posting-{i}" for i in range(12)]
    fetched = []
    eval_calls = 0

    def fake_search(query):
        return SimpleNamespace(results=[SearchResult(url=url) for url in urls])

    def fake_fetch(url):
        fetched.append(url)
        return make_page(url)

    def fake_eval(*, job_candidate, pages):
        nonlocal eval_calls
        eval_calls += 1
        if eval_calls == 1:
            return no_match(job_candidate, pages)
        return one_match(job_candidate, pages)

    monkeypatch.setattr(resolution_module, "search_web", fake_search)
    monkeypatch.setattr(resolution_module, "fetch_web_page", fake_fetch)
    monkeypatch.setattr(resolution_module, "evaluate_job_pages", fake_eval)

    resolved = resolution_module.resolve_job_candidate(candidate)

    assert len(resolved) == 1
    assert len(fetched) == 10
    assert eval_calls == 2
    assert resolved[0].canonical_job_url == urls[5]


def test_stops_at_max_15_fetches_and_returns_unverified(monkeypatch):
    candidate = JobCandidate(
        source="LINKEDIN",
        source_message_id="email-5",
        title="Rare Role",
        company="Rare Company",
        location="Berkeley",
    )

    urls = [f"https://jobs.example.com/posting-{i}" for i in range(30)]
    fetched = []

    monkeypatch.setattr(
        resolution_module,
        "search_web",
        lambda query: SimpleNamespace(
            results=[SearchResult(url=url) for url in urls]
        ),
    )

    def fake_fetch(url):
        fetched.append(url)
        return make_page(url)

    monkeypatch.setattr(resolution_module, "fetch_web_page", fake_fetch)
    monkeypatch.setattr(resolution_module, "evaluate_job_pages", no_match)

    resolved = resolution_module.resolve_job_candidate(candidate)

    assert resolved == []
    assert len(fetched) == 15
    assert candidate.verification_result == JobVerificationResult.UNVERIFIED
    assert candidate.resolution_reason == JobResolutionReason.NO_SUITABLE_POSTING_FOUND
