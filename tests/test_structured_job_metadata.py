from email.message import Message
from io import BytesIO

import job_agent.web.client as web_client

HTML = b'\n<!doctype html>\n<html>\n<head>\n    <title>AI Product Manager | Example AI</title>\n\n    <script type="application/ld+json">\n    {\n        "@context": "https://schema.org",\n        "@type": "JobPosting",\n        "title": "AI Product Manager",\n        "hiringOrganization": {\n            "@type": "Organization",\n            "name": "Example AI"\n        },\n        "identifier": {\n            "@type": "PropertyValue",\n            "name": "Example AI",\n            "value": "REQ-12345"\n        },\n        "jobLocation": {\n            "@type": "Place",\n            "address": {\n                "@type": "PostalAddress",\n                "addressLocality": "San Francisco",\n                "addressRegion": "CA",\n                "addressCountry": "US"\n            }\n        }\n    }\n    </script>\n</head>\n<body>\n    <h1>AI Product Manager</h1>\n    <div>Product Management - San Francisco</div>\n    <p>Build AI products for customers.</p>\n</body>\n</html>\n'


def test_structured_metadata_does_not_pollute_visible_text(monkeypatch):
    class Response(BytesIO):
        status = 200

        def geturl(self):
            return "https://example.com/job"

    response = Response(HTML)
    response.headers = Message()
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    monkeypatch.setattr(web_client, 'urlopen', lambda request, timeout: response)
    snapshot = web_client.fetch_web_page('https://example.com/job')
    assert snapshot.status_code == 200
    assert len(snapshot.job_postings) == 1
    posting = snapshot.job_postings[0]
    assert posting.title == 'AI Product Manager'
    assert posting.company == 'Example AI'
    assert posting.locations == ('San Francisco, CA, US',)
    assert posting.identifier == 'REQ-12345'
    assert '@context' not in snapshot.text
    assert 'REQ-12345' not in snapshot.text
