"""Render GitHub-style Markdown alerts as semantic documentation callouts."""

from __future__ import annotations

import re
from xml.etree import ElementTree as etree

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


ALERT_MARKER = re.compile(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*(?:\n|$)")


class GitHubAlertTreeprocessor(Treeprocessor):
    """Convert GitHub's alert marker at the start of a blockquote."""

    def run(self, root: etree.Element) -> etree.Element:
        for parent in root.iter():
            transformed_children: list[etree.Element] = []
            changed = False
            for child in list(parent):
                if child.tag != "blockquote":
                    transformed_children.append(child)
                    continue
                sections = self._split_alerts(child)
                transformed_children.extend(sections)
                changed = changed or sections != [child]
            if changed:
                parent[:] = transformed_children
        return root

    @staticmethod
    def _split_alerts(quote: etree.Element) -> list[etree.Element]:
        """Split a Markdown-merged quote into one aside per GitHub alert."""
        children = list(quote)
        markers = [
            (index, ALERT_MARKER.match(child.text or ""))
            for index, child in enumerate(children)
            if child.tag == "p" and ALERT_MARKER.match(child.text or "")
        ]
        if not markers:
            return [quote]

        sections: list[etree.Element] = []
        first_marker_index = markers[0][0]
        if first_marker_index:
            plain_quote = etree.Element("blockquote", quote.attrib)
            plain_quote.extend(children[:first_marker_index])
            sections.append(plain_quote)

        for index, (_, marker) in enumerate(markers):
            start = markers[index][0]
            end = markers[index + 1][0] if index + 1 < len(markers) else len(children)
            sections.append(GitHubAlertTreeprocessor._create_alert(marker.group(1).lower(), children[start:end]))
        return sections

    @staticmethod
    def _create_alert(kind: str, children: list[etree.Element]) -> etree.Element:
        """Create one semantic alert, retaining rich Markdown child elements."""
        alert = etree.Element(
            "aside",
            {"class": f"gh-alert gh-alert--{kind}", "role": "note", "aria-label": kind.title()},
        )
        title = etree.SubElement(alert, "div", {"class": "gh-alert__title"})
        icon = etree.SubElement(title, "span", {"aria-hidden": "true"})
        icon.text = "◆"
        label = etree.SubElement(title, "span")
        label.text = kind.upper()

        first_paragraph = children[0]
        first_paragraph.text = ALERT_MARKER.sub("", first_paragraph.text or "", count=1)
        if first_paragraph.text or len(first_paragraph):
            alert.append(first_paragraph)
        alert.extend(children[1:])
        return alert


class GitHubAlertsExtension(Extension):
    """Register GitHub Alert support for Python-Markdown and MkDocs."""

    def extendMarkdown(self, md) -> None:
        md.treeprocessors.register(GitHubAlertTreeprocessor(md), "github-alerts", 15)


def makeExtension(**kwargs) -> GitHubAlertsExtension:
    """Create the extension for Python-Markdown discovery."""
    return GitHubAlertsExtension(**kwargs)
