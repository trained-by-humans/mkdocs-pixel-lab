# Card grids

Use grids to arrange related content in responsive columns. Add cards for
section indexes, landing pages, and collections of next steps.

## Enable

```yaml
markdown_extensions:
  - attr_list
  - md_in_html
```

For highlighted code inside cards, also enable [Code blocks](code-blocks.md#enable).

## List cards

Wrap a Markdown list in a `grid cards` container. Each list item becomes a
card; indent paragraphs and links to keep them inside the same item.

<div class="grid cards" markdown>

- **Get up and running**

    Install Pixel Lab, create your first page, and preview your documentation.

    [Start building →](../getting-started.md)

- **Make it yours**

    Choose the colors, fonts, and branding that fit your project.

    [Explore theme setup →](../setup/index.md)

- **Find your way**

    Organize pages into sections and help readers discover what comes next.

    [Set up navigation →](../setup/navigation.md)

- **Show your work**

    Share examples with highlighted code, line emphasis, and a copy button.

    [Explore code blocks →](code-blocks.md)

- **Explain the details**

    Keep tips, warnings, and supporting information close to the content.

    [Explore admonitions →](admonitions.md)

- **Bring pages to life**

    Add responsive images and video with the theme's pixel borders.

    [Explore media →](media.md)

</div>

```markdown
<div class="grid cards" markdown>

- **Get up and running**

    Install the theme and create your first page.

    [Start building →](../getting-started.md)

- **Make it yours**

    Choose the colors, fonts, and branding that fit your project.

    [Explore theme setup →](../setup/index.md)

</div>
```

Links remain ordinary links: use Tab to reach them and Enter to open them.
On hover, cards lift while their shadow's outer edges stay anchored. With
reduced motion enabled, only the border color changes.

## Rich content

Cards can hold illustrations, prose, links, and code. Each card below is an
explicit block inside the same grid.

<div class="grid" markdown>

<div class="card" markdown>

### A visual explanation

![Source frame, Process signal, and Output result connected in a flow.](../assets/component-preview.svg)

Walk readers through a workflow with an illustration and a short explanation.

[Add images and video →](media.md)

</div>

<div class="card" markdown>

### A practical example

Start with a small configuration and add more as your documentation grows.

```yaml
site_name: My project
theme:
  name: pixel-lab
```

[Read the getting started guide →](../getting-started.md)

</div>

</div>

Use an explicit `.card` wrapper when one card contains several blocks:

````markdown
<div class="grid" markdown>

<div class="card" markdown>

### A practical example

Start with a small configuration.

```yaml
site_name: My project
theme:
  name: pixel-lab
```

[Read the getting started guide →](../getting-started.md)

</div>

</div>
````

## Simple block cards

Short blocks can also become cards, without a surrounding list.

<div class="grid" markdown>

**Keyboard friendly.** Follow ordinary links with Tab and open them with Enter.
{ .card }

**Responsive by default.** Cards form columns when space allows and stack on
smaller screens.
{ .card }

</div>

```markdown
<div class="grid" markdown>

**Keyboard friendly.** Follow ordinary links with Tab and open them with Enter.
{ .card }

**Responsive by default.** Cards stack when the available space is narrow.
{ .card }

</div>
```

## A grid without cards

A generic grid can arrange content without adding borders, surfaces, or shadows.

<div class="grid" markdown>

<div markdown>

### For readers

Browse clear examples, follow related topics, and find the next useful step.

[Browse components →](index.md)

</div>

<div markdown>

### For authors

Write with Markdown and combine existing components to suit your content.

[Read the configuration reference →](../reference/configuration.md)

</div>

</div>

```markdown
<div class="grid" markdown>

<div markdown>

### For readers

Browse examples and discover related topics.

</div>

<div markdown>

### For authors

Write with Markdown and combine existing components.

</div>

</div>
```

## Customization

Use the properties and selectors below to customize this component, following the
[Customization](customization.md) guide.

### Component properties

These CSS variables take their default values from the corresponding theme settings.

| Property | Description | Theme setting | Default |
| --- | --- | --- | --- |
| `--surface` | Card background | `surface_color` | Ivory · `#fffdf2` |
| `--border` | Card outline | `border_color` | Near-black · `#101410` |
| `--shadow` | Card's pixel shadow | `shadow_color` | Near-black · `#101410` |
| `--accent` | Card border on hover | `accent_color` | Leaf green · `#4caf50` |

Card text inherits the page's `text_color`. Set `color` on the card selector
below to change it locally.

See [Colors](../setup/colors.md) for palette configuration and
[Fonts](../setup/fonts.md) for typography defaults and overrides.

### Component styles

Use these selectors to style the grid and its cards. The card selectors cover
both block cards and cards written as list items.

| Selector | CSS properties | Description |
| --- | --- | --- |
| `.grid` | `grid-template-columns`, `gap`, `margin` | The number and width of columns, gaps between cards, and space around the grid |
| `.card, .grid.cards > :is(ul, ol) > li` | `background`, `border`, `box-shadow`, `padding`, `color` | The card surface, frame, content inset, and inherited text color |
| `.card:hover, .grid.cards > :is(ul, ol) > li:hover` | `border-color` | The card outline on hover |
