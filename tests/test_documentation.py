"""Keep the public theme manual buildable and its examples/configuration honest."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from markdown import Markdown
from mkdocs.commands.build import build
from mkdocs.config import load_config


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GUIDES = sorted(
    source
    for section in ("setup", "components")
    for source in (DOCS / section).glob("*.md")
    if source.name != "index.md"
)
PARAMETER_HEADER = "| Parameter | Default | Effect |"


def parameter_rows(source: Path):
    """Read parameter tables only, not live examples of other table formats."""
    yield from parameter_rows_in(source.read_text())


def parameter_rows_in(content: str):
    in_parameters = False
    for line in content.splitlines():
        if line == PARAMETER_HEADER:
            in_parameters = True
            continue
        if not line.startswith("|"):
            in_parameters = False
        if in_parameters:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) == 3 and not cells[0].startswith("---"):
                yield cells


def guide_section(source: Path, heading: str) -> str:
    """Select an authored H2 section, including its H3 subsections."""
    selected = []
    found = False
    fence = None
    for line in source.read_text().splitlines(keepends=True):
        marker = re.match(r"^(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        elif marker:
            fence = (marker[1][0], len(marker[1]))
        elif line.startswith("## "):
            if found:
                break
            found = line.rstrip("\n") == f"## {heading}"
            continue
        if found:
            selected.append(line)
    assert found, (source, heading)
    return "".join(selected)


@pytest.fixture(scope="module")
def documentation_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("documentation")
    config = load_config(
        config_file=str(ROOT / "mkdocs.yml"),
        site_dir=str(destination),
        strict=True,
    )
    build(config)
    return destination


def test_public_documentation_builds_all_pages(documentation_dir: Path) -> None:
    for source in DOCS.rglob("*.md"):
        relative = source.relative_to(DOCS)
        output = (
            relative.with_suffix(".html")
            if source.name == "index.md"
            else relative.with_suffix("") / "index.html"
        )
        assert (documentation_dir / output).is_file(), relative
    assert (documentation_dir / "search/search_index.json").is_file()
    assert (documentation_dir / "assets/component-preview.svg").is_file()
    assert not (documentation_dir / "theme-coverage-results.json").exists()


def test_troubleshooting_has_a_dedicated_reference_page(documentation_dir: Path) -> None:
    config = load_config(config_file=str(ROOT / "mkdocs.yml"))
    reference = next(item["Reference"] for item in config.nav if "Reference" in item)
    entries = {name: path for item in reference for name, path in item.items()}
    assert entries["Troubleshooting"] == "reference/troubleshooting.md"
    assert list(entries).index("Troubleshooting") == list(entries).index("Compatibility") + 1
    content = (DOCS / "reference/troubleshooting.md").read_text()
    assert content.startswith("# Troubleshooting\n")
    headings = [
        "A component looks like plain text",
        "A custom icon looks too small or like a filled box",
        "Source links point at the wrong branch",
        "Search has no results",
        "A bundled plugin is missing",
    ]
    assert re.findall(r"^## (.+)$", content, re.MULTILINE) == headings
    compatibility = (DOCS / "reference/compatibility.md").read_text()
    assert "[Troubleshooting](troubleshooting.md)" in compatibility
    assert "## Troubleshooting\n" not in compatibility
    assert all(heading not in compatibility for heading in headings)
    rendered = (documentation_dir / "reference/troubleshooting/index.html").read_text()
    for heading in headings:
        anchor = heading.lower().replace(" ", "-")
        assert f'<h2 id="{anchor}">{heading}' in rendered


def test_documented_theme_defaults_match_implementation() -> None:
    reference = (DOCS / "reference/configuration.md").read_text()
    defaults_section = reference.split("## Theme defaults\n", 1)[1]
    example = re.search(r"```yaml\n(.*?)\n```", defaults_section, re.DOTALL)
    assert example is not None
    documented = yaml.safe_load(example.group(1))["theme"]
    actual = yaml.safe_load((ROOT / "src/mkdocs_pixel_lab/mkdocs_theme.yml").read_text())
    assert documented == actual


def test_documentation_yaml_examples_are_valid() -> None:
    for source in DOCS.rglob("*.md"):
        for match in re.finditer(r"^```yaml\n(.*?)\n```$", source.read_text(), re.MULTILINE | re.DOTALL):
            assert yaml.safe_load(match.group(1)) is not None, source


def test_color_examples_match_the_site_default_palette() -> None:
    defaults = yaml.safe_load((ROOT / "src/mkdocs_pixel_lab/mkdocs_theme.yml").read_text())
    config = load_config(config_file=str(ROOT / "mkdocs.yml"))
    colors = {key: value for key, value in defaults.items() if key.endswith("_color") or key == "header_background"}
    for key, value in colors.items():
        assert config.theme[key] == value, key
    for source in DOCS.rglob("*.md"):
        for match in re.finditer(r"^```yaml\n(.*?)\n```$", source.read_text(), re.MULTILINE | re.DOTALL):
            example = yaml.safe_load(match.group(1))
            if not isinstance(example, dict):
                continue
            for key, value in example.get("theme", {}).items():
                if key in colors:
                    assert value == colors[key], (source, key)


def test_components_have_syntax_and_relevant_appearance_options() -> None:
    for source in (DOCS / "components").glob("*.md"):
        if source.name == "index.md":
            continue
        content = source.read_text()
        if source.name == "metadata.md":
            assert "## Customization\n" not in content, source
            assert "## Site defaults\n" in content, source
            assert "## Automatic defaults\n" in content, source
        else:
            assert "## Customization\n" in content, source
        assert "```markdown\n" in content, source


@pytest.mark.parametrize(
    ("section", "name", "wrapper", "component"),
    [
        ("components", "admonitions", "instance-admonition", '<div class="admonition note">'),
        ("components", "alerts", "instance-alert", 'class="gh-alert gh-alert--tip"'),
        ("components", "code-blocks", "instance-code", 'class="language-python highlight"'),
        ("components", "details", "instance-details", '<details class="note">'),
        ("setup", "heading-permalinks", "instance-heading", '<h2 id="a-specific-section">'),
        ("components", "media", "instance-media", '<img '),
        ("components", "tables", "instance-table", '<table>'),
        ("components", "tabs", "instance-tabs", 'class="tabbed-set tabbed-alternate"'),
        ("components", "text", "instance-quote", '<blockquote>'),
    ],
)
def test_component_and_scoped_overrides_render(
    documentation_dir: Path, section: str, name: str, wrapper: str, component: str,
) -> None:
    source = DOCS / section / f"{name}.md"
    heading = "Further customization" if section == "setup" else "Customization"
    customization = guide_section(source, heading)
    theme_settings, overrides = customization.split("### Component-wide overrides\n", 1)
    component_scope, scoped_overrides = overrides.split("### Scoped overrides\n", 1)
    assert "### Customize the component\n" not in customization
    assert "### Override an instance" not in customization
    assert PARAMETER_HEADER in theme_settings
    assert "```css\n" not in theme_settings
    assert "index.md#load-custom-css" in component_scope
    assert "index.md#scope-selected-instances" in scoped_overrides
    all_css = re.findall(r"```css\n(.*?)\n```", component_scope, re.DOTALL)
    scoped_css = re.findall(r"```css\n(.*?)\n```", scoped_overrides, re.DOTALL)
    assert all_css and scoped_css
    assert all("instance-" not in css for css in all_css)
    assert all(css.lstrip().startswith(f".{wrapper}") for css in scoped_css)
    example = re.search(r"(?P<fence>`{3,})markdown\n(.*?)\n(?P=fence)", scoped_overrides, re.DOTALL)
    assert example is not None
    config = load_config(config_file=str(ROOT / "mkdocs.yml"))
    html = Markdown(
        extensions=config.markdown_extensions, extension_configs=config.mdx_configs,
    ).convert(example[2])
    assert html.startswith(f'<div class="{wrapper}">')
    assert 'markdown="1"' not in html
    assert component in html
    reused_html = Markdown(
        extensions=config.markdown_extensions, extension_configs=config.mdx_configs,
    ).convert(f"{example[2]}\n\n{example[2]}")
    assert reused_html.count(f'<div class="{wrapper}">') == 2
    rendered = (documentation_dir / section / name / "index.html").read_text()
    anchor = heading.lower().replace(" ", "-")
    assert f'<h2 id="{anchor}">{heading}' in rendered
    assert 'id="customize-the-component"' not in rendered
    assert '<h3 id="component-wide-overrides">Component-wide overrides' in rendered
    assert '<h3 id="scoped-overrides">Scoped overrides' in rendered
    assert 'id="override-an-instance"' not in rendered


def test_alerts_and_admonitions_have_separate_guides() -> None:
    config = load_config(config_file=str(ROOT / "mkdocs.yml"))
    components = next(item["Components"] for item in config.nav if "Components" in item)
    entries = {name: path for item in components for name, path in item.items()}
    assert entries["Alerts"] == "components/alerts.md"
    assert entries["Admonitions"] == "components/admonitions.md"
    assert list(entries).index("Admonitions") == list(entries).index("Alerts") + 1
    for name, title, extension in (
        ("alerts", "Alerts", "mkdocs_pixel_lab.github_alerts"),
        ("admonitions", "Admonitions", "admonition"),
    ):
        source = DOCS / "components" / f"{name}.md"
        assert source.read_text().startswith(f"# {title}\n")
        example = re.search(r"```yaml\n(.*?)\n```", guide_section(source, "Enable"), re.DOTALL)
        assert example is not None
        assert yaml.safe_load(example.group(1))["markdown_extensions"] == [extension]
    alerts = DOCS / "components/alerts.md"
    admonitions = DOCS / "components/admonitions.md"
    alert_options = {row[0] for row in parameter_rows(alerts)}
    admonition_options = {row[0] for row in parameter_rows(admonitions)}
    assert "`alert_tip_color`" in alert_options
    assert "`highlight_color`" not in alert_options and "`surface_color`" not in alert_options
    assert "`highlight_color`" in admonition_options and "`surface_color`" in admonition_options
    assert not any(parameter.startswith("`alert_") for parameter in admonition_options)
    assert "[admonition](admonitions.md)" in alerts.read_text()
    assert "[Alerts](alerts.md)" in admonitions.read_text()
    assert "[Collapsible content](details.md)" in admonitions.read_text()


def test_nested_shadow_guidance_belongs_to_container_guides(documentation_dir: Path) -> None:
    overview = guide_section(DOCS / "components/index.md", "Nest components")
    assert "shadows" in overview and "outer container" in overview
    for name in ("tabs", "alerts", "admonitions", "details", "tables"):
        source = DOCS / "components" / f"{name}.md"
        content = source.read_text()
        notes = re.findall(r"> \[!NOTE\]\n>\n((?:>[^\n]*\n)+)", content)
        assert any("shadow" in note and "index.md#nest-components" in note for note in notes), source
        rendered = (documentation_dir / "components" / name / "index.html").read_text()
        assert 'class="gh-alert gh-alert--note"' in rendered, source
    for name in ("media", "code-blocks"):
        source = DOCS / "components" / f"{name}.md"
        assert not re.search(r"(?:nested|inner|inside)[^\n]{0,80}shadow", source.read_text(), re.IGNORECASE), source


def test_common_stylesheet_and_wrapper_setup_is_centralized() -> None:
    overview = DOCS / "components/index.md"
    scopes = guide_section(overview, "Customization scopes")
    assert "extra_css:" in scopes
    assert "  - md_in_html\n" in scopes
    assert "**Component-wide overrides**" in scopes
    assert "**Scoped overrides**" in scopes
    assert "one or several instances" in scopes
    assert "### Scope selected instances\n" in scopes
    assert "Override an instance" not in scopes
    for source in (DOCS / "components").glob("*.md"):
        if source.name == "index.md":
            continue
        for match in re.finditer(r"^```yaml\n(.*?)\n```$", source.read_text(), re.MULTILINE | re.DOTALL):
            example = yaml.safe_load(match[1])
            assert "extra_css" not in example, source
            assert example.get("markdown_extensions") != ["md_in_html"], source


def test_appearance_guides_link_to_common_attributes(documentation_dir: Path) -> None:
    reference = DOCS / "reference/configuration.md"
    common = guide_section(reference, "Common attributes")
    assert "site-wide" in common and "multiple components" in common
    assert "[Colors](../setup/colors.md)" in common
    assert "[Fonts](../setup/fonts.md)" in common
    assert "[Icons](../setup/icons.md)" in common
    rendered = (documentation_dir / "reference/configuration/index.html").read_text()
    assert '<h2 id="common-attributes">Common attributes' in rendered
    for source in GUIDES:
        heading = next(
            (title for title in ("Customization", "Further customization") if f"## {title}\n" in source.read_text()),
            None,
        )
        if heading is None:
            continue
        section = guide_section(source, heading)
        assert section.count("[Common attributes](../reference/configuration.md#common-attributes)") == 1, source
        assert not re.search(
            r"shared (?:tokens|theme settings|theme colors)|"
            r"(?:tokens|colors) (?:are shared|also affect)|"
            r"affect other (?:components|site sections)",
            section,
            re.IGNORECASE,
        ), source


def test_main_configuration_tables_stay_with_their_instructions() -> None:
    sections = {
        "setup/navigation.md": {"Configure navigation": ("`nav`",)},
        "setup/branding.md": {
            "Site name": ("`site_name` (MkDocs)",),
            "Favicon": ("`favicon`",),
            "Footer": ("`footer_text`",),
        },
        "setup/search.md": {"Enable search": ("`plugins` → `search`",)},
        "setup/repository.md": {
            "Repository button": ("`repo_url`", "`repo_name`"),
            "Page source and editing": ("`edit_uri`", "`edit_uri_template`"),
            "Control visibility": ("`show_repo`", "`show_repo_name`", "`show_source`", "`show_edit`"),
        },
        "setup/related-sites.md": {
            "Items": (
                "`items`", "`catalog`",
                "`items[].title` / `catalog.title`", "`items[].url` / `catalog.url`", "`items[].active`",
            ),
            "Footer": ("`show_footer`", "`footer_size`", "`footer_label`"),
            "Header: inline": ("`header_mode`", "`header_size`"),
            "Header: dropdown": ("`dropdown_label`", "`icon.sites`", "`icon.dropdown`"),
        },
        "setup/analytics.md": {
            "Enable GA4": ("`provider`", "`measurement_id`", "`privacy_policy`", "`enabled`", "`site_url`"),
            "Shared consent": ("`consent_domain`",),
        },
        "setup/heading-permalinks.md": {"Enable": ("`permalink`",)},
        "components/metadata.md": {
            "Write metadata": ("`title`", "`description`"),
            "Site defaults": ("`site_name`", "`site_description`"),
            "Automatic defaults": ("`plugins` → `pixel-lab/metadata`",),
        },
    }
    for path, headings in sections.items():
        source = DOCS / path
        all_parameters = [row[0] for row in parameter_rows(source)]
        for heading, parameters in headings.items():
            section = guide_section(source, heading)
            assert "```" in section, (source, heading, "missing configuration example")
            documented = {row[0] for row in parameter_rows_in(section)}
            for parameter in parameters:
                assert parameter in documented, (source, heading, parameter)
                assert all_parameters.count(parameter) == 1, (source, parameter, "duplicated explanation")


def test_customization_tables_cover_appearance_not_feature_setup() -> None:
    defaults = yaml.safe_load((ROOT / "src/mkdocs_pixel_lab/mkdocs_theme.yml").read_text())
    appearance_options = {
        key for key in defaults if key.endswith("_color") or key == "header_background"
    } | {f"icon.{key}" for key in defaults["icon"]} | {
        "permalink_title", "permalink_leading",
        "items[].icon", "catalog.icon", "items[].icon_hover", "catalog.icon_hover",
    }
    for source in GUIDES:
        heading = next(
            (title for title in ("Customization", "Further customization") if f"## {title}\n" in source.read_text()),
            None,
        )
        if heading is None:
            continue
        rows = list(parameter_rows_in(guide_section(source, heading)))
        assert rows, (source, "empty customization reference")
        for parameter, default, effect in rows:
            keys = re.findall(r"`([^`]+)`", parameter)
            assert keys and set(keys) <= appearance_options, (source, parameter)


def test_feature_guides_use_further_customization(documentation_dir: Path) -> None:
    for name in ("branding", "navigation", "heading-permalinks", "search", "repository", "related-sites", "analytics"):
        source = DOCS / "setup" / f"{name}.md"
        content = source.read_text()
        assert content.count("## Further customization\n") == 1, source
        assert "## Customization\n" not in content, source
        rendered = (documentation_dir / "setup" / name / "index.html").read_text()
        assert '<h2 id="further-customization">Further customization' in rendered, source


def test_related_sites_explains_items_before_presentations(documentation_dir: Path) -> None:
    source = DOCS / "setup/related-sites.md"
    headings = re.findall(r"^## (.+)$", source.read_text(), re.MULTILINE)
    assert headings == ["Items", "Footer", "Header: inline", "Header: dropdown", "Further customization"]
    dropdown = guide_section(source, "Header: dropdown")
    assert "### Item icons\n" in dropdown and "### Toolbar icons\n" in dropdown
    parameters = {row[0] for row in parameter_rows_in(dropdown)}
    assert {"`items[].icon` / `catalog.icon`", "`items[].icon_hover` / `catalog.icon_hover`"} <= parameters
    shared = list(parameter_rows_in(guide_section(source, "Further customization")))
    assert all(parameter.endswith('_color`') for parameter, default, effect in shared)
    rendered = (documentation_dir / "setup/related-sites/index.html").read_text()
    anchors = ["items", "footer", "header-inline", "header-dropdown", "item-icons", "toolbar-icons", "further-customization"]
    positions = [rendered.index(f'id="{anchor}"') for anchor in anchors]
    assert positions == sorted(positions)


def test_setup_and_component_guides_have_parameter_tables(documentation_dir: Path) -> None:
    for source in GUIDES:
        assert PARAMETER_HEADER in source.read_text(), source
        assert list(parameter_rows(source)), source
        relative = source.relative_to(DOCS).with_suffix("") / "index.html"
        rendered = (documentation_dir / relative).read_text()
        for header in ("Parameter", "Default", "Effect"):
            assert f"<th>{header}</th>" in rendered, (source, header)


def test_parameter_table_theme_defaults_match_implementation() -> None:
    defaults = yaml.safe_load((ROOT / "src/mkdocs_pixel_lab/mkdocs_theme.yml").read_text())
    checked = set()
    for source in GUIDES:
        for parameter, default, effect in parameter_rows(source):
            key = re.fullmatch(r"`([^`]+)`", parameter)
            if key is None:
                continue
            key = key.group(1)
            path = key.split(".")
            actual = defaults
            for part in path:
                if not isinstance(actual, dict) or part not in actual:
                    break
                actual = actual[part]
            else:
                value = re.search(r"`([^`]+)`", default)
                assert value is not None, (source, key)
                expected = (
                    "null" if actual is None
                    else str(actual).lower() if isinstance(actual, bool)
                    else '""' if actual == ""
                    else str(actual)
                )
                assert value.group(1) == expected, (source, key)
                assert effect, (source, key)
                if key.endswith("_color") or key == "header_background":
                    assert default.split("`", 1)[0].strip(), (source, key, "missing color name")
                checked.add(key)
    assert {"icon.repo", "icon.edit", "show_source", "tab_hover_color", "header_border_color"} <= checked


def test_icon_parameters_are_grouped_by_location(documentation_dir: Path) -> None:
    content = (DOCS / "setup/icons.md").read_text()
    toolbar, page = content.split("## Toolbar icons\n", 1)[1].split("## Page icons\n", 1)
    page = page.split("## Other artwork\n", 1)[0]
    pattern = r"^\| `(icon\.[a-z]+)` \|"
    assert re.findall(pattern, toolbar, re.MULTILINE) == [
        "icon.repo", "icon.search", "icon.menu", "icon.close", "icon.sites", "icon.dropdown",
    ]
    assert re.findall(pattern, page, re.MULTILINE) == ["icon.view", "icon.edit"]
    rendered = (documentation_dir / "setup/icons/index.html").read_text()
    assert 'id="toolbar-icons"' in rendered and 'id="page-icons"' in rendered


def test_component_examples_render(documentation_dir: Path) -> None:
    tabs = (documentation_dir / "components/tabs/index.html").read_text()
    assert 'id="basic-tabs"' in tabs and 'class="tabbed-set tabbed-alternate"' in tabs
    assert 'id="layout-tabs"' in tabs and 'id="forced-tabs"' in tabs
    assert 'class="tabs-padded"' in tabs
    alerts = (documentation_dir / "components/alerts/index.html").read_text()
    for kind in ("note", "tip", "important", "warning", "caution"):
        assert f"gh-alert--{kind}" in alerts
    assert 'class="admonition note"' not in alerts
    admonitions = (documentation_dir / "components/admonitions/index.html").read_text()
    assert 'class="admonition note"' in admonitions
    details = (documentation_dir / "components/details/index.html").read_text()
    assert '<details class="note">' in details
    assert '<details class="tip" open="open">' in details
    code = (documentation_dir / "components/code-blocks/index.html").read_text()
    assert 'class="hll"' in code


def test_setup_and_component_navigation_are_separate(documentation_dir: Path) -> None:
    config = load_config(config_file=str(ROOT / "mkdocs.yml"))
    setup = next(item["Theme setup"] for item in config.nav if "Theme setup" in item)
    components = next(item["Components"] for item in config.nav if "Components" in item)
    assert all(path.startswith("setup/") for item in setup for path in item.values())
    assert all(path.startswith("components/") for item in components for path in item.values())
    tabs = (documentation_dir / "components/tabs/index.html").read_text()
    assert "accent_color" in tabs and "tab_hover_color" in tabs
    assert 'id="customization"' in tabs


def test_heading_setup_is_separate_from_markdown_syntax(documentation_dir: Path) -> None:
    config = load_config(config_file=str(ROOT / "mkdocs.yml"))
    setup = next(item["Theme setup"] for item in config.nav if "Theme setup" in item)
    components = next(item["Components"] for item in config.nav if "Components" in item)
    setup_entries = {name: path for item in setup for name, path in item.items()}
    assert setup_entries["Heading permalinks"] == "setup/heading-permalinks.md"
    assert not any("heading" in path for item in components for path in item.values())
    assert not (DOCS / "components/heading-links.md").exists()
    permalink = DOCS / "setup/heading-permalinks.md"
    assert permalink.read_text().startswith("# Heading permalinks\n")
    assert "## Write headings\n" not in permalink.read_text()
    enable = re.search(r"```yaml\n(.*?)\n```", guide_section(permalink, "Enable"), re.DOTALL)
    assert enable is not None
    assert yaml.safe_load(enable[1])["markdown_extensions"] == [{"toc": {"permalink": True}}]
    text = DOCS / "components/text.md"
    headings = guide_section(text, "Headings")
    assert "# Page title\n\n## A section\n\n### A subsection" in headings
    assert "../setup/heading-permalinks.md" in headings
    assert "../components/text.md#headings" in permalink.read_text()
    rendered = (documentation_dir / "components/text/index.html").read_text()
    assert '<h2 id="headings">Headings' in rendered
    rendered_setup = (documentation_dir / "setup/heading-permalinks/index.html").read_text()
    assert '<h1 id="heading-permalinks">Heading permalinks' in rendered_setup
