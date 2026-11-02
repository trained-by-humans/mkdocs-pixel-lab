# Pixel Lab → Zensical migration

Companion to the [successor evaluation](README.md). Assessed
2026-10-25 against Pixel Lab 0.2.0 (`d48084c`), Zensical 0.0.72 and Python
3.12/macOS. This page contains Zensical-specific features, evidence, the
implementation plan and preview instructions; versions have not been rechecked
during the editorial cleanup.

## Goal and status

Add a separately tested Zensical integration while preserving Pixel Lab's
appearance, URLs, Markdown components and existing MkDocs users. Switch our own
documentation deployment only after the implementation gates below pass.

Pixel Lab 0.2.0 has no supported Zensical installation yet. The
[preview instructions](#run-the-isolated-preview) build a disposable source copy
outside the repository, leaving production configuration unchanged. The
production integration/build wrapper remains proposed work.

## Priorities after parity

Prioritize native multilingual search, then benchmark incremental rebuilds and
assess Markdown/`llms.txt` exports. Social cards, blog/tags/API views and offline
downloads need separate UI acceptance work. See the
[feature table](#new-features-and-fixes-value-to-us) for benefits and limitations.
The component/module system remains roadmap work, not a migration dependency.

## New features and fixes: value to us

| Capability or recent fix | Value to Pixel Lab | What migration would still require |
| --- | --- | --- |
| Rust engine and incremental rebuilds | Potentially useful for large sites | No comparative benchmark was run; exploratory build timings do not establish a speedup |
| New multilingual client-side search, offline support, highlighting and exclusions | **Potentially high**; an alternative to our MkDocs/Lunr integration | Build a compatible search UI/adapter. Search UI localization is currently English-only according to its docs |
| Native blog, tags, social cards, redirects, navigation and API plugin replacements | Useful future product options | Native replacements do not execute arbitrary plugins; several features depend on templates/UI we do not supply |
| `llms.txt`, Markdown exports, Copy as Markdown | Medium if machine-readable documentation becomes a requirement | Exports and discovery/UI integration need verification with Pixel Lab |
| Privacy plugin support in 0.0.72 | Low immediate benefit | Asset downloading/rewriting is distinct from our analytics consent behavior; we already bundle fonts locally |
| Same-second template edits and filesystem watcher fixes in 0.0.72 | Useful for development | These fix Zensical behavior; they are not proof of an equivalent MkDocs defect |
| SuperFences extension ordering, HTML entity/URL rewriting and trailing-slash Markdown link fixes in 0.0.72 | Relevant to our Markdown and link handling | Compatibility fixes in the new engine; acceptance coverage is still needed |
| `exclude_docs`, `draft_docs`, `not_in_nav` support in 0.0.70 | Required compatibility groundwork | These are existing MkDocs concepts, not new functionality relative to our baseline |
| Search accessibility and instant navigation UI improvements | Useful design references | Bundled Zensical UI changes do not automatically improve Pixel Lab's independent JS and HTML |
| `rustls` security update in 0.0.72 | Good maintenance signal | Fixes a dependency of Zensical, which Pixel Lab does not currently use |

Dark mode, deeper navigation, localization, and other missing Pixel Lab UI
features are still theme work. Switching generators alone does not add them to
our templates.

## Implementation plan

Each phase should leave the MkDocs build usable. These PRs are proposed work;
they have not been created.

### 1. Dependencies and engine-independent helpers

- Extract `page_metadata` and its parser/constants from the module that imports
  `mkdocs.plugins`. Keep the existing plugin as an adapter around that helper.
- Extract/reuse the Git lookup helper without requiring MkDocs imports.
- Test PyMdown 11 and 12 against our alerts, tabs, code blocks and permalinks.
  Broaden the base bound only for versions that pass.
- Add a Zensical install path that enforces Python 3.11+. One possible first
  step is an optional extra on our existing package; its mandatory MkDocs
  dependency would still install both engines. A separate integration package
  can avoid that later.

**Exit:** ordinary resolver installation and `pip check` pass; existing MkDocs
tests still pass. No `--no-deps` in supported installation instructions.

### 2. Templates, configuration and assets

- Replace map `.get()` with bracket lookup plus `default`, preserving false,
  empty-string and null semantics. Use filters/suffix comparison for string
  methods; put incompatible source-link/sitemap logic in engine-specific partials.
- Convert MiniJinja split results with `split('/') | list` before indexing;
  join the remainder to preserve slash-containing branches/source paths.
- Adapt the sitemap to Page objects and decide whether to add a dedicated 404
  template; inheriting Material's template alone does not integrate our layout.
- Preserve title deduplication, source/edit URLs, icon escaping, disabled
  controls, tab layouts and analytics consent behavior.
- Normalize icon/font defaults, ensure nested relative URLs work, and filter
  non-public theme files from the output.
- Keep a separate Zensical configuration/output directory for preview builds.

**Exit:** strict fixture and docs builds pass; output URL manifest matches the
baseline for authored pages; assets load at both `/` and a project subpath.

### 3. Native search integration

- Build a small bridge around the pinned native search client, mounting its
  dialog in a shadow root and resolving index locations against `base_url`.
  Keep the MkDocs loader and Material frontend bundle out of this integration.
- Replace the old search panel/listeners rather than leaving two active search
  implementations. Style the dialog for Pixel Lab and update the trigger's
  accessible state/description to match its actual controlled dialog.
- Handle index/worker failures visibly. Define lazy-loading behavior and restore
  focus to the trigger when search closes.
- Ship the client/CSS/worker and license notices as a matched, pinned set.
  Add an upgrade check because these exports can change.

**Exit:** home/nested/subpath searches, result navigation, keyboard selection,
Escape, focus return, no-results and failed-load states pass in the browser.
No unintended remote requests. Offline support is a separate gate.

### 4. Replace plugin behavior

| Existing plugin | Proposed Zensical equivalent | Acceptance |
| --- | --- | --- |
| `pixel-lab/metadata` | Python-Markdown postprocessor, sharing our parser; namespaced `page.meta.pixel_lab_metadata` consumed by templates | Explicit fields win, first eligible paragraph fallback, length/escaping/title deduplication, no Git calls. Pin and guard the internal context adapter |
| `pixel-lab/robots` | Opt-in build finalizer that creates robots only if neither source nor output owns one; alternatively a site-owned `docs/robots.txt` for our docs | Preserve existing files; correct sitemap URL including project subpath; no write to source docs |
| `pixel-lab/git-lastmod` | Opt-in finalizer with a source-to-output manifest, shared Git lookup and a Zensical sitemap writer | Tracked/renamed files, literal paths, shallow clones, generated pages, canonical URLs, correct per-file dates and rebuild refresh |

The metadata proof uses Zensical's internal rendering-context interface. Keep it
behind a version-specific adapter with a clear error when the interface changes.
The native `meta` replacement handles inherited metadata; it is not a replacement
for our introductory-paragraph extraction.

For the finalizers, document one canonical build command that runs Zensical and
then the requested finalizers. Its preview/watch path must also rerun them after
changes. An ordinary `zensical serve` invocation alone must not be advertised as
providing these post-build features. Do not assign the current date to pages
whose Git history is unavailable.

**Exit:** all three features either have parity tests and a working preview path
or are explicitly unavailable in the published Zensical support matrix. Full
migration of this project should retain the metadata behavior we currently use;
sites using the optional Git/robots plugins must resolve those before cutover.

### 5. CI, packaging and preview deployment

- Add Zensical build/browser jobs starting with Python 3.12, then verify every
  supported interpreter from Python 3.11 upward before advertising support.
- Keep existing MkDocs API/plugin tests on MkDocs. They do not become Zensical
  tests merely because a Zensical command succeeds in another job.
- Exercise clean wheel installation, theme entry-point discovery, strict builds,
  artifact contents and the documented build/finalizer command.
- Build a preview artifact in a configured `site_dir`, such as
  `build/docs-zensical`, without changing the live Pages upload path.
- Compare representative desktop/mobile screenshots; exercise custom icons,
  colors, source links, related-site navigation and analytics consent branches.
- Establish cold-build and edit-rebuild timings after correctness passes; record
  versions and hardware. The exploratory timings are not a fair benchmark.

**Exit:** installable artifact and documented configuration pass CI; preview is
reviewable; unsupported behavior is stated explicitly.

### 6. Documentation cutover and release

- Update installation, compatibility, plugin, troubleshooting and workflow docs.
- Publish an integration release and migration notes with tested version bounds.
- Change the Pages build command and uploaded directory together, retaining
  checkout history (`fetch-depth: 0`) if Git dates are enabled.
- Keep `actions/upload-pages-artifact` / `actions/deploy-pages` for static
  publishing; use the documented build wrapper when finalizers are enabled.
- Keep `mkdocs.yml` during initial adoption; TOML conversion is optional.
- Preserve `site_url`, authored page paths and existing navigation.
- Keep the previous engine/configuration available during adoption; rollback is
  a workflow/config revert followed by rebuilding the prior artifact.

**Exit:** deployed URL/asset/search checks pass; consumers can choose the engine
without an unannounced change to the current MkDocs behavior.

## Runtime evidence

Initial checks used the unmodified package. The adapted preview below explores
how to address those failures; it does not certify the published distribution.

| Check | Result |
| --- | --- |
| Joint install resolution: Pixel Lab 0.2.0 + Zensical 0.0.72 | **Fail**: PyMdown `<11` versus `>=11.0` |
| Zensical strict fixture build after installing Pixel Lab with `--no-deps` for diagnosis | **Fail**: sitemap template line 4 |
| Zensical strict documentation build in the same diagnostic environment | **Fail**: same sitemap error |
| Zensical effective plugin configuration | All three `pixel-lab/*` plugin entries are discarded, including `pixel-lab/metadata` when present in the input YAML |

The Zensical diagnostic environment is intentionally outside our supported
dependency bounds; its failure is not a supported installation result. It
exposes additional porting work beyond the independently confirmed resolver
conflict. Copies of the docs and fixture were placed under temporary project
roots, because Zensical requires `docs_dir` to be within its project root.

### Zensical preview findings

Further exploration used copied templates, the Zensical 0.0.72 wheel and
[UI source pinned to this commit](https://github.com/zensical/ui/tree/f2e8d027764f7f52272a7064e80c576af5f08de9)
(UI 0.0.38). The preview loads the theme through `custom_dir` with `name: null`,
without installing Pixel Lab's distribution; its environment passes `pip check`.
This bypasses the published package's dependency conflict for exploration.

| Area | Confirmed finding / preview result |
| --- | --- |
| Templates | MiniJinja rejects map `.get()` and string `.lower()`, `.endswith()`, `.split()`. Bracket/default expressions and filters work; `split` needs `list` before length/indexing |
| Sitemap | Uses Page objects rather than MkDocs Files with `.page`. The native template emits all five fixture canonical URLs, without Git dates |
| Icons and fonts | Modern icon names become broken image URLs in our macros. `variant: classic` preserves null-icon fallbacks; `font: false` keeps our bundled-font setup |
| Asset filtering | Copied theme directories can publish Python, bytecode and theme config. Native `exclude` patterns remove those artifacts |
| Strict builds | Adapted fixture and documentation builds both pass |
| Search | Native index is `search.json` with `config`/`items`. A bridge using UI exports `setup`, `mount`, `open` returns `/guide/code/` for `highlighting` from home and a nested page; Escape closes the dialog |
| Mobile navigation | Opens/closes with Escape; browser smoke recorded no JavaScript exceptions |
| Automatic metadata | A Markdown postprocessor reuses our parser through internal `ContextPreprocessor` and stores `page.meta.pixel_lab_metadata`. Docs home description is correctly derived from its introduction |
| Missing output | Preview supplies neither Git sitemap dates, generated robots nor a dedicated `404.html` |

**Limits:** these are targeted checks on Python 3.12/macOS, not a supported
distribution or complete test matrix. The search dialog retains Zensical styling;
focus return, trigger ARIA state, failure states, full visual parity and
live-reload parity need acceptance checks. Search uses `fetch` and is HTTP-only;
offline `file://` behavior is unverified. Native result grouping differs from
MkDocs, so identical result counts are not required. Client exports and the
metadata context are version-specific implementation details.
The helper extracts the pure parser from `metadata.py` into the temporary
project; a release must use a shared source module instead of that extraction.

## Run the isolated preview

The [preparation helper](../experiments/zensical/prepare_preview.py) adapts copied
templates and adds prototype search/metadata bridges. It does not satisfy the
release gates above. Use these steps to reproduce the exploration.

### 1. Create an isolated environment

Run from the Pixel Lab checkout. Python 3.11+ is required by Zensical; use 3.12
to reproduce our checks. On systems without `python3.12`, substitute the path
to that interpreter.

```sh
pixel_repo="$PWD"
zensical_preview_root="$(mktemp -d /tmp/pixel-lab-zensical.XXXXXX)"
python3.12 -m venv "$zensical_preview_root/venv"
"$zensical_preview_root/venv/bin/python" -m pip install 'zensical==0.0.72'
"$zensical_preview_root/venv/bin/python" -m pip check
```

Do not install `mkdocs-pixel-lab` into this environment. The preview uses
`theme.name: null` plus `theme.custom_dir` to load the copied theme and
`PYTHONPATH` to load the existing standalone Markdown-alert extension.
This avoids the published distribution's conflicting dependency requirements.

### 2. Obtain the matching search UI source

The native client currently ships in the UI source as minified JS plus CSS.
The helper expects this exact inspected commit (UI version 0.0.38). It also uses
the worker bundled in the Zensical 0.0.72 wheel. No frontend build is needed.

```sh
git clone https://github.com/zensical/ui.git "$zensical_preview_root/ui"
git -C "$zensical_preview_root/ui" checkout --detach f2e8d027764f7f52272a7064e80c576af5f08de9
```

The helper copies the upstream license notice.

### 3. Prepare and build the small fixture

```sh
"$zensical_preview_root/venv/bin/python" experiments/zensical/prepare_preview.py \
  --fixture \
  --ui-source "$zensical_preview_root/ui" \
  --destination "$zensical_preview_root/fixture"

PYTHONPATH="$zensical_preview_root/fixture:$pixel_repo/src" \
  "$zensical_preview_root/venv/bin/zensical" build --strict --clean \
  --config-file "$zensical_preview_root/fixture/mkdocs.yml"
```

The destination must be empty and outside the repository. Run preparation once
per destination; choose a new destination if you want to start again. The
helper's expression rewrites are tailored to the assessed Pixel Lab source,
rather than a general Jinja migration tool.

### 4. Preview and check behavior

```sh
PYTHONPATH="$zensical_preview_root/fixture:$pixel_repo/src" \
  "$zensical_preview_root/venv/bin/zensical" serve \
  --config-file "$zensical_preview_root/fixture/mkdocs.yml"
```

Open the address printed by the server. Check:

- Search for `highlighting` from the home page and `/guide/code/`. Both should
  return a link to the code-highlighting page. Search uses a separate dialog.
- Open a result, verify its URL, and close search with Escape.
- At a narrow viewport, open the mobile menu and close it with Escape.
- Inspect network/console errors and check that no icon requests go to
  `/lucide/...` or `/material/...`.
- Inspect generated files: no `.py`, `.pyc`, `__pycache__`, or
  `mkdocs_theme.yml` should be published.

Use the implementation gates above for full component, metadata and visual checks.

The preview copies source docs. Edit the copied Markdown to experiment with
`serve`; changes to the original repository are not automatically recopied.

### 5. Prepare the actual documentation

Omit `--fixture` and use a fresh destination:

```sh
"$zensical_preview_root/venv/bin/python" experiments/zensical/prepare_preview.py \
  --ui-source "$zensical_preview_root/ui" \
  --destination "$zensical_preview_root/docs-preview"

PYTHONPATH="$zensical_preview_root/docs-preview:$pixel_repo/src" \
  "$zensical_preview_root/venv/bin/zensical" build --strict --clean \
  --config-file "$zensical_preview_root/docs-preview/mkdocs.yml"
```

Output is `$zensical_preview_root/docs-preview/site`. This is a local preview
artifact, not the directory consumed by our current Pages workflow.

Stop the local server to return to the existing MkDocs workflow. Temporary
files can be retained for comparison or removed when no longer needed.

## Preview configuration

The generated configuration includes:

```yaml
docs_dir: docs
site_dir: site
theme:
  name: null
  custom_dir: overrides
  variant: classic
  font: false
plugins:
  - search
  - exclude:
      glob:
        - '**/*.py'
        - '**/*.pyc'
        - '**/__pycache__/**'
        - mkdocs_theme.yml
```

It also retains the original Markdown extensions and adds a prototype metadata
extension. The original `pixel-lab/*` plugin entries are replaced explicitly.

## Site-owned robots and Git dates

For a site-owned robots policy, a normal `docs/robots.txt` can be copied as a
static asset. For our public documentation, an example is:

```text
User-agent: *
Allow: /

Sitemap: https://trained-by-humans.github.io/mkdocs-pixel-lab/sitemap.xml
```

Use the site's own URL for another deployment. A site-owned file replaces the
need for generation only for that site; it does not port the optional plugin.

Git dates require the [planned finalizer/source manifest](#4-replace-plugin-behavior).
The preview omits `lastmod`; keep that omission until actual Git dates are available.

## Troubleshooting

| Symptom | Cause / action |
| --- | --- |
| PyMdown resolver conflict | The current published theme was installed; start with the isolated source-preview environment above |
| `unknown method: map has no method named get` | An unadapted template is being used; check `custom_dir` and rerun preparation into a fresh directory |
| `string has no method named lower/split` | Python-style string methods remain in a template; use the adapted copy |
| `cannot calculate length ... iterator` | Convert `split` output with `list` before length/index operations |
| Sitemap failure involving `file.page` | The MkDocs sitemap template is still active; the preview uses Zensical's Page-based version |
| Broken `lucide/...` image URLs | Modern icon defaults entered Pixel Lab's URL macros; use the preview's `classic` defaults or explicit tested asset URLs |
| `docs_dir must be within project root` | Put copied docs underneath the temporary configuration root; do not point an external config at repository docs |
| Search index exists but search does not work | The native index alone is insufficient; verify the module bridge, CSS, worker and nested base URL |
| `metadata_bridge` or `mkdocs_pixel_lab` cannot be imported | Both the temporary project root and original `src` directory must be in the command's `PYTHONPATH` |
| Plugins configured but output missing | Unsupported MkDocs plugins are silently ignored; use replacements rather than relying on strict mode |
| Unexpected visual differences | This prototype is not a visual-parity implementation; compare the unchanged MkDocs build and track gaps before cutover |

## Sources

- [Zensical 0.0.72 release](https://github.com/zensical/zensical/releases/tag/v0.0.72)
- [Zensical release history](https://github.com/zensical/zensical/releases)
- [Zensical MkDocs migration guide](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Zensical plugin compatibility, including ignored plugins](https://zensical.org/docs/compatibility/mkdocs/plugins/)
- [Zensical search behavior](https://zensical.org/docs/setup/search/)
- [Zensical package metadata](https://pypi.org/pypi/zensical/0.0.72/json)
- [Zensical theme packaging and overrides](https://zensical.org/docs/customization/)
- [Zensical offline limitations](https://zensical.org/docs/setup/offline/)
- [UI source used by the prototype](https://github.com/zensical/ui/tree/f2e8d027764f7f52272a7064e80c576af5f08de9)
