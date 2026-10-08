"""Metadata precedence, readable excerpts, and static HTML integration."""

from html.parser import HTMLParser
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config import load_config
import pytest

from mkdocs_pixel_lab.metadata import DESCRIPTION_LENGTH, page_metadata


FIXTURE = Path(__file__).parent / "fixture_site" / "mkdocs.yml"


def test_explicit_fields_win_and_are_not_shortened():
    description = "Explicit description " * 20
    result = page_metadata(
        "<h1>Automatic heading</h1><p>Automatic description.</p>",
        meta={"title": " Custom   title ", "description": description},
        page_title="Navigation label",
        site_name="Site",
        site_description="Site description",
    )
    assert result == {"title": "Custom title", "description": description.strip()}


@pytest.mark.parametrize("invalid", [None, "", " \n\t ", [], {}, False, 123])
def test_invalid_fields_fall_back_to_page_content(invalid):
    assert page_metadata(
        "<h1>Page heading</h1><p>Page introduction.</p>",
        meta={"title": invalid, "description": invalid},
        page_title="Navigation label",
        site_description="Site description",
    ) == {"title": "Page heading", "description": "Page introduction."}


def test_plain_text_retains_inline_code_and_links_but_not_permalink_icons():
    result = page_metadata(
        '<h1>Guide &amp; setup<a class="headerlink" href="#guide">¶</a></h1>'
        '<p>Use <a href="/">ML</a> &amp; <code>predict()</code> safely.<br>Next step.</p>'
    )
    assert result == {"title": "Guide & setup", "description": "Use ML & predict() safely. Next step."}


@pytest.mark.parametrize(
    "block",
    [
        '<table><tbody><tr><td><p>Table text</p></td></tr></tbody></table>',
        '<pre><code>Code text</code></pre>',
        '<aside class="gh-alert"><p>Alert text</p></aside>',
        '<blockquote><p>Quoted text</p></blockquote>',
        '<div class="admonition"><p>Admonition text</p></div>',
        '<details><summary>Summary</summary><p>Details text</p></details>',
        '<nav><p>Navigation text</p></nav>',
        '<ul><li><p>List text</p></li></ul>',
        '<div class="tabbed-set"><p>Tab text</p></div>',
        '<div hidden><p>Hidden text</p></div>',
        '<p><img src="image.png" alt="Image-only paragraph"></p>',
        '<figure><figcaption><p>Caption text</p></figcaption></figure>',
        '<script>const html = "<p>Script text</p>";</script>',
        '<style>p { color: red; }</style>',
    ],
)
def test_components_are_not_used_as_introductory_prose(block):
    result = page_metadata(f"<h1>Page</h1>{block}<p>Actual introduction.</p>")
    assert result == {"title": "Page", "description": "Actual introduction."}


def test_first_heading_and_paragraph_are_used():
    result = page_metadata("<h1>First</h1><p>First paragraph.</p><h1>Second</h1><p>Second paragraph.</p>")
    assert result == {"title": "First", "description": "First paragraph."}


def test_generated_description_is_shortened_at_a_word_boundary():
    paragraph = " ".join(f"word{index}" for index in range(100))
    description = page_metadata(f"<p>{paragraph}</p>")["description"]
    assert len(description) <= DESCRIPTION_LENGTH
    assert description.endswith("…")
    assert paragraph.startswith(description[:-1] + " ")


def test_empty_body_falls_back_to_mkdocs_and_site_fields():
    assert page_metadata("", page_title="Page label", site_name="Site", site_description="Site intro.") == {
        "title": "Page label", "description": "Site intro."
    }
    assert page_metadata("", site_name="Site") == {"title": "Site", "description": ""}


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.descriptions = []
        self.canonicals = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and attrs.get("name") == "description":
            self.descriptions.append(attrs.get("content"))
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def build_page(tmp_path, markdown, *, automatic=True, site_description="Site fallback."):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(markdown, encoding="utf-8")
    plugins = ["search", "pixel-lab/metadata"] if automatic else ["search"]
    config = load_config(
        config_file=str(FIXTURE),
        docs_dir=str(docs),
        site_dir=str(tmp_path / "site"),
        nav=[{"Short label": "index.md"}],
        plugins=plugins,
        site_name="Metadata Site",
        site_description=site_description,
        site_url="https://example.invalid/docs/",
        strict=True,
    )
    build(config)
    html = (tmp_path / "site" / "index.html").read_text(encoding="utf-8")
    head = HeadParser()
    head.feed(html)
    return html, head


@pytest.mark.parametrize("automatic", [True, False])
def test_explicit_metadata_is_escaped_and_independent_of_visible_titles(tmp_path, automatic):
    html, head = build_page(tmp_path, '''---
title: 'SEO "title" & <example>'
description: 'A "quoted" description & <example>.'
---

# Visible heading

Visible body.
''', automatic=automatic)
    assert head.title == 'SEO "title" & <example> — Metadata Site'
    assert head.descriptions == ['A "quoted" description & <example>.']
    assert head.canonicals == ["https://example.invalid/docs/"]
    assert '<h1 id="visible-heading">Visible heading' in html
    assert '>Short label</a>' in html
    assert '<example>' not in html


def test_build_uses_heading_and_plain_paragraph_without_front_matter(tmp_path):
    _, head = build_page(tmp_path, "# Actual heading\n\nUse **bold**, `code`, and [links](https://example.com/).")
    assert head.title == "Actual heading — Metadata Site"
    assert head.descriptions == ["Use bold, code, and links."]


def test_metadata_plugin_never_runs_git(tmp_path, monkeypatch):
    def unexpected_git(*args):
        pytest.fail("The metadata-only plugin must not run Git commands")

    monkeypatch.setattr("mkdocs_pixel_lab.git_lastmod._git", unexpected_git)
    _, head = build_page(tmp_path, "# Git-free heading\n\nA content-based description.")
    assert head.title == "Git-free heading — Metadata Site"
    assert head.descriptions == ["A content-based description."]


@pytest.mark.parametrize("title", ["Metadata Site", "Guide — Metadata Site"])
def test_site_name_is_not_appended_twice(tmp_path, title):
    _, head = build_page(tmp_path, f"---\ntitle: {title}\n---\n\n# Visible heading")
    assert head.title == title


@pytest.mark.parametrize("automatic", [True, False])
def test_missing_description_does_not_emit_an_empty_tag(tmp_path, automatic):
    _, head = build_page(tmp_path, "# Heading", automatic=automatic, site_description=" ")
    assert head.descriptions == []
