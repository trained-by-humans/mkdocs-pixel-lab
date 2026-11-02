# MkDocs’ sudden end of life

> Evaluated **2026-10-25**, against Pixel Lab **0.2.0**, commit `d48084c`.
> Runtime checks used Python 3.12 on macOS. This is a migration assessment;
> the package, production theme, configuration, and workflows were not migrated.

The apparent end of active MkDocs 1 maintenance has prompted us to assess
a sustainable path for Pixel Lab. The evidence behind that assessment is:

- The latest published MkDocs release remains **1.6.1, 2024-08-30**. Its latest
  default-branch commit observed during this evaluation is dated **2025-10-20**.
  The repository is not archived.
- The last active MkDocs maintainer describes the original project as
  unmaintained and maintains ProperDocs as a compatible continuation. This is
  the maintainer's statement, rather than a guarantee about future development.
- A separate **MkDocs 2 preview** exists. Its published examples use a different
  page/template contract. It is not evidence that our MkDocs 1 theme and plugins
  will work unchanged.
- Material for MkDocs and the wider plugin ecosystem are separate projects;
  lack of MkDocs core releases does not mean they have all stopped development.

## Candidates

| Candidate | Current evidence | Compatibility with Pixel Lab | Useful additions | Decision |
| --- | --- | --- | --- | --- |
| **ProperDocs 1.6.7** | Published 2026-03-20; repository updated in October; continuation by the last active MkDocs maintainer | High, with a confirmed search selector mismatch. Both strict builds and 111 selected tests pass. | Live reload and URL/anchor validation fixes; Python 3.14 support; removal of an unmaintained dependency | **Preferred next engine**, after search adaptation and a compatibility CI job |
| **Zensical 0.0.72** | Published 2026-10-23; frequent releases; created by the Material for MkDocs team | Partial. Theme entry point is discovered, but our sitemap fails; custom plugins are ignored; PyMdown requirements conflict. | Incremental Rust build engine; new multilingual search; built-in plugin replacements; Markdown exports and social cards | **Defer migration**; evaluate a separate port if these capabilities become priorities |
| **DocsForge 13.0.4** | Published 2026-10-23; small, independent project created in May 2026; vendors a ProperDocs/MkDocs engine and a Material fork | Unverified. Its reviewed dependency metadata requires PyMdown 11.0.1+, conflicting with our `<11` bound. Its principal target is Material sites. | Bundled search, math, diagrams, blog, offline features, bilingual documentation, announcement configuration | **Do not adopt for Pixel Lab now**; its bundled frontend is less useful to a theme that supplies its own UI |
| **MkDocs 2 preview** | Original author's Version 2 discussion and separate preview documentation; PyPI's latest MkDocs release is still 1.6.1 | Unverified and structurally different: preview uses `templates/base.html`, `page.html`, and `page.toc.title`; Pixel Lab uses MkDocs 1 contexts and plugin events | Simpler website-oriented workflow and GitHub Flavored Markdown are described | **Do not select as a compatible upgrade** without released APIs and a porting assessment |
| **Sphinx + MyST** | Maintained Python documentation ecosystem; Sphinx 9.2.0 released 2026-10-21 | Theme and plugins require porting; Markdown also needs MyST compatibility review | Strong cross-references, API documentation, multiple output formats | Consider only if API/reference publishing becomes the product's main focus |
| **Docusaurus / VitePress** | Maintained React/MDX and Vue/Vite documentation stacks | Existing Python theme/plugin entry points do not carry over; templates, build configuration, search, and extensions need replacement | Component ecosystems; Docusaurus offers versioning/i18n, VitePress offers Vue components and Vite tooling | Alternatives for a deliberate product rewrite, rather than a continuation of this Python theme |

Sphinx, Docusaurus, and VitePress are alternatives, not MkDocs-compatible forks.
No runtime builds were attempted for those three or DocsForge.

## Pixel Lab requirements

A migration must preserve the following contracts. These requirements define
what we need from a successor and the checks needed before switching engines.

| Requirement | What must be preserved or verified |
| --- | --- |
| Python support | Retain Python 3.10 support for existing MkDocs users; document any higher minimum for a separate integration |
| Dependency compatibility | Normal package installation and `pip check` must pass. Pixel Lab 0.2.0 currently requires PyMdown `>=10,<11`; wider bounds need component tests |
| Configuration | Preserve `mkdocs.yml`, navigation, theme options, repository/edit URLs and site metadata, or document explicit migration steps |
| Theme installation | Discover the packaged theme through its entry point and include all required templates, fonts, icons, CSS and JavaScript |
| Template behavior | Preserve page/navigation contexts, title handling, source/edit actions, custom icons and escaping across the template engine |
| Markdown components | Render GitHub alerts, admonitions, details, tabs, highlighted code and heading permalinks with their existing behavior |
| Automatic metadata | Preserve explicit-field precedence and introductory-content fallbacks provided by `pixel-lab/metadata` |
| Sitemap and Git dates | Preserve canonical URLs, including project/version subpaths; retain optional per-file Git dates and omit unavailable history without fabricating dates |
| Robots policy | Preserve site-owned `robots.txt`; retain optional generation and the correct sitemap URL |
| Search | Keep working search from home and nested pages, correct result destinations and a compatible index/loader/UI integration |
| Browser interaction | Preserve responsive navigation, keyboard behavior, focus handling, copy controls and analytics consent; verify representative desktop/mobile pages |
| Plugin integration | Execute our three bundled plugins or provide tested replacements with documented behavior |
| Development and publishing | Provide strict builds, useful validation, reliable preview/rebuild behavior and a documented CI/Pages deployment path |
| Verification and packaging | Exercise the selected engine in API/CLI tests, test the built wheel, and publish only intended assets with stable authored URLs |

Candidate-specific results are in the [ProperDocs evaluation](properdocs.md#runtime-evidence)
and the [Zensical preview findings](zensical.md#zensical-preview-findings).

## Recommended Migration Path

**No evaluated candidate has demonstrated complete, unchanged compatibility
with all of Pixel Lab's requirements.** ProperDocs is the closest match, but
its search loader still needs an integration fix. Other frameworks require a
broader port or have not been verified against our theme and plugins.

**Move first to a maintained fork of the original MkDocs, such as ProperDocs.**
It preserves the architecture and APIs we already use while restoring a path
for maintenance fixes. This gives us a smaller migration to validate before
considering a framework with different templates, plugins or frontend behavior.
Retain compatibility for existing MkDocs consumers during that move.

After stabilizing on the maintained fork, evaluate another framework only if
its capabilities address concrete needs that remain unmet. Zensical is one
option: its adapted preview is promising, but a production migration still
requires the work in the [migration guide](zensical.md).

ProperDocs retains the MkDocs architecture while adding live-reload, validation and URL
handling fixes. See the [benefits and limits](properdocs.md#benefits-and-limits)
and [implementation plan](properdocs.md#implementation-plan), including
the search fix required before switching production.

## Migration documents

| Document | Contents |
| --- | --- |
| This evaluation | Successor comparison, Pixel Lab requirements and recommended migration path |
| [ProperDocs migration](properdocs.md) | Benefits, implementation plan, test evidence, reproduction commands and rollback |
| [Zensical migration](zensical.md) | Features, test findings, implementation plan, preview commands and troubleshooting |
| [Preview helper](../experiments/zensical/prepare_preview.py) | Prepares a disposable adapted theme and docs copy |

These documents describe the October 25 assessment; package versions and
compatibility have not been re-evaluated as part of the October 28 editorial cleanup.

## Sources

Engine-specific references are collected in the [ProperDocs](properdocs.md#sources)
and [Zensical](zensical.md#sources) migration guides.

- [MkDocs 1.6.1 release](https://github.com/mkdocs/mkdocs/releases/tag/1.6.1)
- [MkDocs default-branch history](https://github.com/mkdocs/mkdocs/commits/master/)
- [DocsForge source, stated scope, and limitations](https://github.com/QQSHI13/docsforge)
- [DocsForge 13.0.4 release](https://github.com/QQSHI13/docsforge/releases/tag/v13.0.4)
- [MkDocs Version 2 discussion](https://github.com/mkdocs/mkdocs/discussions/4077)
- [MkDocs 2 preview documentation](https://www.encode.io/mkdocs/)
- [Sphinx documentation](https://www.sphinx-doc.org/), [MyST parser](https://myst-parser.readthedocs.io/)
- [Docusaurus documentation](https://docusaurus.io/docs), [VitePress documentation](https://vitepress.dev/guide/what-is-vitepress)
