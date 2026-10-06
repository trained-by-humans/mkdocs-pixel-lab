"""Privacy links work independently of tracking and on nested pages."""

from html import unescape
from pathlib import Path
import re

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"


@pytest.mark.parametrize("analytics_enabled", [False, True])
@pytest.mark.parametrize("policy_url,expected", [
    (None, None),
    ("", None),
    ("   ", None),
    ("https://example.com/privacy/", "https://example.com/privacy/"),
    (" https://example.com/privacy/?source=docs&lang=en ", "https://example.com/privacy/?source=docs&lang=en"),
    ("privacy/", "privacy/"),
])
def test_privacy_link_configuration(tmp_path, analytics_enabled, policy_url, expected):
    analytics = {
        "provider": "google", "measurement_id": "G-TEST123456", "enabled": analytics_enabled,
    }
    if policy_url is not None:
        analytics["privacy_policy"] = policy_url
    config = load_config(
        config_file=str(FIXTURE), site_dir=str(tmp_path),
        extra={"analytics": analytics},
    )
    build(config)
    active = analytics_enabled and expected is not None

    for page, prefix in [("index.html", ""), ("guide/media/index.html", "../../")]:
        html = (tmp_path / page).read_text()
        links = [unescape(href) for href in re.findall(
            r'<a\b[^>]*\bhref="([^"]*)"[^>]*>Privacy policy</a>', html,
        )]
        if expected is None:
            assert not links
            assert 'class="privacy-policy"' not in html
        else:
            target = prefix + expected if expected == "privacy/" else expected
            assert links == [target] * (2 if active else 1)
            assert 'class="privacy-policy"' in html
        assert ('id="analytics-consent"' in html) == active
        assert ('id="analytics-settings"' in html) == active
        assert ('src="assets/js/analytics.js"' in html or 'src="../../assets/js/analytics.js"' in html) == active
