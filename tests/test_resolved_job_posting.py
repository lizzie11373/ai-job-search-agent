from job_agent.models.job_candidate import (
    JobCandidate,
    JobVerificationResult,
)

from job_agent.models.resolved_job_posting import (
    JobDeduplicationResult,
    ResolvedJobPosting,
)




def test_independent_postings_promote_to_independent_opportunities():
    """Domain supports multiple postings; current resolver stops on the first match."""
    job_candidate = JobCandidate(
        source="MOCK_JOB_ALERT",
        source_message_id="email-001",
        title="Product Manager",
        company="Example AI",
        location="San Francisco",
        source_url="https://provider.example/jobs/123",
        source_item_id="123",
    )


    posting_a = ResolvedJobPosting(
        source_candidate=job_candidate,
        posting_url=(
            "https://careers.example.ai/jobs/pm-shopping"
        ),
        jd_text=(
            "Product Manager, Shopping. "
            "Build AI shopping experiences."
        ),
        posting_title="Product Manager, Shopping",
        posting_company="Example AI",
        posting_location="San Francisco",
    )


    posting_b = ResolvedJobPosting(
        source_candidate=job_candidate,
        posting_url=(
            "https://careers.example.ai/jobs/pm-agents"
        ),
        jd_text=(
            "Product Manager, Agents. "
            "Build AI agent experiences."
        ),
        posting_title="Product Manager, Agents",
        posting_company="Example AI",
        posting_location="San Francisco",
    )


    resolved_postings = [
        posting_a,
        posting_b,
    ]


    # Domain can represent multiple postings; current resolution stops at first match.
    job_candidate.verification_result = (
        JobVerificationResult.VERIFIED
    )


    assert len(resolved_postings) == 2

    assert (
        posting_a.source_candidate
        is job_candidate
    )

    assert (
        posting_b.source_candidate
        is job_candidate
    )

    assert (
        posting_a.canonical_job_url
        != posting_b.canonical_job_url
    )

    assert (
        posting_a.jd_text
        != posting_b.jd_text
    )


    # Canonical dedupe is now posting-level state.
    posting_a.deduplication_result = (
        JobDeduplicationResult.NEW
    )

    posting_b.deduplication_result = (
        JobDeduplicationResult.NEW
    )


    opportunity_a = (
        posting_a.promote_to_job_opportunity(
            opportunity_id="J101"
        )
    )

    opportunity_b = (
        posting_b.promote_to_job_opportunity(
            opportunity_id="J102"
        )
    )


    assert (
        opportunity_a.opportunity_id
        == "J101"
    )

    assert (
        opportunity_b.opportunity_id
        == "J102"
    )

    assert (
        opportunity_a.canonical_job_url
        == posting_a.canonical_job_url
    )

    assert (
        opportunity_b.canonical_job_url
        == posting_b.canonical_job_url
    )

    assert (
        opportunity_a.canonical_job_url
        != opportunity_b.canonical_job_url
    )

    assert (
        opportunity_a.title
        == "Product Manager, Shopping"
    )

    assert (
        opportunity_b.title
        == "Product Manager, Agents"
    )


    # The discovery lead no longer owns canonical job state.
    assert not hasattr(
        job_candidate,
        "canonical_job_url",
    )

    assert not hasattr(
        job_candidate,
        "jd_text",
    )

    assert not hasattr(
        job_candidate,
        "deduplication_result",
    )
