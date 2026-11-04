# Card grids

## List syntax

<div class="grid cards" id="list-cards" markdown="1">

- **Fast setup**

    Install the theme and start writing. [Get started](#)

- **Just Markdown**

    Write pages in plain Markdown.

</div>

## Block syntax

<div class="grid" id="block-cards" markdown="1">

Plain card text
{ .card }

Card with a [link](#)
{ .card }

</div>

## Code inside a card

<div class="grid" id="code-cards" markdown="1">

<div class="card" markdown>

```python
print("a very long line of code that should scroll inside the card instead of breaking the layout or overflowing the page")
```

</div>

Short card
{ .card }

</div>

## Grid inside a panel

<div class="pixel-panel" id="nested-block-panel" markdown="1">

<div class="grid" markdown>

Inner card one
{ .card }

Inner card two
{ .card }

</div>

</div>

## Padded panel

<div class="pixel-panel" id="padded-list-panel" style="padding: 20px" markdown="1">

<div class="grid cards" markdown>

- **Card one**
- **Card two**

</div>

</div>

## Ordered list inside a panel

<div class="pixel-panel" id="ordered-list-panel" style="padding: 20px" markdown="1">

<div class="grid cards" markdown="1">

1. **First step**
2. **Second step**

</div>

</div>
