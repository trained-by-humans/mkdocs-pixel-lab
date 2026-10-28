# Component alignment

## Full-width components

```text
Code establishes the full-width frame and shadow alignment.
```

> [!NOTE]
>
> A note alert.

> [!TIP]
>
> A tip alert.

> [!IMPORTANT]
>
> An important alert.

> [!WARNING]
>
> A warning alert.

> [!CAUTION]
>
> A caution alert.

!!! note "Admonition"

    A regular note.

???+ note "Details"

    Expanded details.

=== "Tab"

    A padded tab panel.

<div id="wide-table" markdown="1">

| Wide payload | Status |
| --- | --- |
| `a_very_long_unbroken_payload_that_exceeds_even_the_desktop_column_width_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ` | Ready |

</div>

![Wide Markdown image](../assets/alignment-wide.svg)

[![Linked wide Markdown image](../assets/alignment-wide.svg)](../assets/alignment-wide.svg)

<video width="2000" controls preload="metadata" poster="../../assets/alignment-wide.svg" aria-label="Wide video">
  <source src="../../assets/pixel-lab-demo.mp4" type="video/mp4">
</video>

<div class="pixel-panel">A full-width panel.</div>

<div class="example">A full-width example card.</div>

<div class="pixel-panel install">A full-width installation panel.</div>

> An ordinary quote has no shadow and reaches the content boundary.

## Intrinsic sizes

<div id="small-table" markdown="1">

| A | B |
| --- | --- |
| 1 | 2 |

</div>

<p><img src="../../assets/alignment-wide.svg" width="80" alt="Small image"></p>

<div class="hero-flow"><div class="node">Source</div><span class="arrow">→</span><div class="node">Output</div></div>

<div id="wide-node" class="hero-flow"><div class="node">A_long_unbroken_node_label_that_must_wrap_without_pushing_its_shadow_past_the_content_boundary_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ</div></div>

## Nested components

!!! note "Outer frame"

    > [!NOTE]
    >
    > Nested alert.

    ![Nested wide image](../assets/alignment-wide.svg)

    <img src="../../assets/alignment-wide.svg" alt="Direct nested wide image">

    | Nested | Table |
    | --- | --- |
    | `a_very_long_unbroken_nested_payload_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789_abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ` | B |
