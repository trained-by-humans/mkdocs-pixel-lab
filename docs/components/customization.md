# Customization

Tables, tabs, notes, and other components use the theme's colors and spacing
by default. You can adjust their appearance to suit your content, whether you
want all your tables to share a color or one particular note to stand out.

This guide walks through changing the color of table headers, loading your
styles, and applying a change to selected tables. Along the way, you'll find
live examples and links to the CSS used to style them. You can use the same
approach with the properties and selectors in each component guide's
Customization section.

For the overall look of your site, including its palette, fonts, and branding,
start with [Theme setup](../setup/index.md). Here, we'll look at how those
settings affect components before making changes to individual component styles.

The approaches below give you different levels of control over where a change
applies:

| Approach | Scope of changes | Method |
| --- | --- | --- |
| [Theme overrides](#theme-overrides) | Every component that uses the setting, throughout the site | Set values in the `theme` section of `mkdocs.yml`. |
| [Component overrides](#component-overrides) | All instances of one component, such as every table | Add a CSS rule for that component to your custom stylesheet. |
| [Instance overrides](#instance-overrides) | Selected components on one or several pages | Wrap the selected Markdown in a named class and target that class in your stylesheet. |

## Theme overrides

Theme overrides change shared appearance values in the `theme` section of
`mkdocs.yml`. Several components can use the same setting, which helps keep
their appearance consistent across your site. Each component guide's Component
properties table describes the CSS variables it uses and lists their theme
settings and default values.

For example, tables get their outer border color from `border_color`. If
you'd like those borders to be red, you can add the setting to the existing
`theme` section in `mkdocs.yml`:

```yaml
theme:
  name: pixel-lab
  border_color: "#e60012"
```

This also changes the outlines of code blocks, notes, and other components,
because they use the same setting. For a walkthrough of the theme's shared
colors, see [Colors](../setup/colors.md). For typography defaults and overrides,
see [Fonts](../setup/fonts.md).

## Component overrides

A component override changes the appearance of every occurrence of a
particular component throughout your documentation. You define the style
with CSS and load it through your MkDocs configuration.

### Define custom CSS

Each component guide provides two references:

- Component properties lists CSS variables, their descriptions, and the theme
  settings that supply their defaults. See [Table properties](tables.md#component-properties).
- Component styles lists selectors for the parts you can style and the CSS
  properties you can change. See [Table styles](tables.md#component-styles).

Choose a selector and either override a component variable or set a CSS property.
For example, this rule gives every table header a red background with white text:

```css
/* Keep the selector; edit or add properties to change the appearance. */
.main th {              /* Selector */
  --surface2: #e60012;   /* Component property: value */
  color: #ffffff;       /* CSS property: value */
}
```

Overriding a variable changes the styles that use it within the selected part.
Setting a CSS property directly changes that property on the selected element.
To keep a property connected to a theme variable, use `var(--surface2)` as its
value instead of a fixed color.

For all styles defined by the theme, see the
[theme stylesheet source](https://github.com/trained-by-humans/mkdocs-pixel-lab/blob/main/src/mkdocs_pixel_lab/assets/css/style.css).

### Load custom CSS

Save your CSS rules in a stylesheet. Create `docs/stylesheets/components.css`
in your project, along with any missing folders, and add the rule above.
For a project using the default `docs` folder, the files should look like this:

```text
your-project/
├── mkdocs.yml
└── docs/
    └── stylesheets/
        └── components.css
```

Then add the following to `mkdocs.yml` so MkDocs loads it:

```yaml
extra_css:
  - stylesheets/components.css
```

If you already have an `extra_css` list, add the stylesheet path to it.

## Instance overrides

An instance override applies a style to selected occurrences of a component.
Give them a named wrapper and use it in your selector to limit where the
rule applies. The properties work the same way as in a component override.

### Scope selected instances

We'll use an HTML wrapper to give selected components a class name. To allow
Markdown inside that wrapper, add `md_in_html` to your existing
`markdown_extensions` list in `mkdocs.yml`:

```yaml
markdown_extensions:
  - md_in_html
```

With `md_in_html` enabled, you can wrap ordinary Markdown inside a `<div markdown>` wrapper.

### Define and load custom CSS

Use the same approach as [Define custom CSS](#define-custom-css), but scope
the selector to your wrapper's class. For this table, replace `.main` with
`.instance-table`:

```css
.instance-table th {
  --surface2: #e60012;
  color: #ffffff;
}
```

The properties stay the same; only the scope changes. Follow [Load custom CSS](#load-custom-css)
to add this rule to your stylesheet.

### Apply custom CSS to a component

In your Markdown page, wrap the table in a `<div>` with the matching
`instance-table` class. Keep blank lines around the table so it renders correctly:

```markdown
<div class="instance-table" markdown>

| Setting | Value |
| --- | --- |
| Enabled | Yes |
| Retries | 3 |

</div>
```

Reuse the wrapper wherever you want this style. For a live result and the
files behind it, see [the Pixel Lab site example](#example-the-pixel-lab-site).

## Example: the Pixel Lab site

This documentation site uses the same approach described above. It keeps the
theme's default settings and loads a custom stylesheet to style selected
components. The table below uses the `instance-table` wrapper and its CSS rule:

<div class="instance-table" markdown>

| Setting | Value |
| --- | --- |
| Enabled | Yes |
| Retries | 3 |

</div>

For comparison, this table has no wrapper and shows the default appearance
on this site:

| Setting | Value |
| --- | --- |
| Enabled | Yes |
| Retries | 3 |

You can follow the setup in the site's source files:

- [Site configuration](https://github.com/trained-by-humans/mkdocs-pixel-lab/blob/main/mkdocs.yml)
  enables `md_in_html` and loads `stylesheets/customization.css` through `extra_css`.
- The [example CSS source](../stylesheets/customization.css) contains the
  scoped rule that styles the wrapped table.
- The [Markdown source of this page](https://github.com/trained-by-humans/mkdocs-pixel-lab/blob/main/docs/components/customization.md)
  shows the wrapper around the table.

## Preview your changes

As you work, run `mkdocs serve` and keep a page with your component open in
the browser. MkDocs refreshes the preview when you save your Markdown or
stylesheet. If you've changed `mkdocs.yml`, wait for the preview to rebuild
before checking the result.

For a style applied through a wrapper, compare a wrapped component with one
outside it. It's also useful to narrow the browser window and check that the
content still fits comfortably.

If nothing changes, first check that the CSS file is saved at the path listed
in `extra_css`. Then check that the class name in your Markdown matches the
one in your selector.

To inspect a selected component, see
[Chrome DevTools](https://developer.chrome.com/docs/devtools/css/).

## How overrides work together

- Theme settings provide the shared appearance. Your custom stylesheet loads
  afterward, so you can override selected properties while keeping the rest.
- More specific selectors take priority. When selectors are equally specific,
  the later rule wins. In these examples, `.main th` and `.instance-table th`
  are equally specific, so place the instance rule after the general rule.
- Wrappers limit where instance rules apply. General rules still apply outside
  the wrapper; use only the instance rule if other components should keep their
  theme appearance.
- CSS variables such as `--accent` can affect nested components. Set properties
  directly on the element when you need a more targeted change. See
  [Nest components](index.md#nest-components).
