import pytest

from job_agent.search.providers.qwen_web_search import _normalize_search_source_url


@pytest.mark.parametrize(
    'value,expected',
    [
        ('https://aprecruit.berkeley.edu/JPF05327', 'https://aprecruit.berkeley.edu/JPF05327'),
        ('  https://example.com/careers/job/  ', 'https://example.com/careers/job/'),
        ('/&nbsp;..."\x02\x10', None),
        ('/relative/path', None),
        ('https://example.com/a raw space', None),
        ('javascript:void(0)', None),
    ],
)
def test_search_url_boundary(value, expected):
    assert _normalize_search_source_url(value) == expected
