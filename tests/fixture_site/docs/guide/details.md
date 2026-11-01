# Details layouts

## Pymdown details

<!-- Minimal reproduction of the code-only expand at:
https://ultralytics.ml-pipes.com/tutorials/isolate_segmented_objects/ -->
<div id="pym-code" markdown="1">

??? note "Define the IsolateObjects operator"

    ```python
    def isolate_objects(image, masks):
        return [image * mask for mask in masks]  # A long line exercises scrolling without widening the expandable frame.
    ```

</div>

<div id="pym-table" markdown="1">

???+ tip "Table, initially open"

    | Payload | Result |
    | --- | --- |
    | `a_very_long_unbroken_payload_name_to_exercise_horizontal_scrolling_in_a_narrow_details_body` | Isolated object |

</div>

<div id="pym-prose" markdown="1">

???+ note "Prose"

    Keep a comfortable inset for explanations.

</div>

<div id="pym-mixed" markdown="1">

???+ note "Mixed content"

    Explanation before code.

    ```python
    print("Mixed content stays padded")
    ```

</div>

<div id="pym-multiple" markdown="1">

???+ note "Multiple blocks"

    ```text
    First block
    ```

    ```text
    Second block
    ```

</div>

## Native HTML

<details id="raw-code" open>
<summary>Raw code</summary>
<!-- Comments and whitespace do not count as content blocks. -->
<pre><code>A long raw code line exercises horizontal scrolling without widening the expandable frame or losing its internal code padding.</code></pre>
</details>

<details id="raw-table">
<summary>Raw table</summary>
<table><thead><tr><th>Payload</th><th>Result</th></tr></thead>
<tbody><tr><td>a_very_long_unbroken_payload_name_to_exercise_horizontal_scrolling_in_a_narrow_details_body</td><td>Isolated object</td></tr></tbody></table>
</details>

<details id="raw-prose" open>
<summary>Raw prose</summary>
<p>Keep a comfortable inset for explanations.</p>
</details>

<details id="raw-mixed" open>
<summary>Raw mixed content</summary>
<p>Explanation before code.</p>
<pre><code>Mixed content stays padded.</code></pre>
</details>

<details id="raw-multiple" open>
<summary>Raw multiple blocks</summary>
<pre><code>First block</code></pre>
<pre><code>Second block</code></pre>
</details>

<details id="raw-text" open>
<summary>Text nodes also count</summary>
An unwrapped explanation.
<pre><code>One element with a text sibling stays padded.</code></pre>
</details>

## Explicit overrides

<div id="pym-padded-code" class="details-padded" markdown="1">

???+ note "Padded code"

    ```python
    print("Explicit inset")
    ```

</div>

<div id="pym-padded-table" class="details-padded" markdown="1">

???+ note "Padded table"

    | Setting | Value |
    | --- | --- |
    | Inset | Padded |

</div>

<div id="pym-flush-mixed" class="details-flush" markdown="1">

???+ note "Flush mixed content"

    Explicitly remove the surrounding inset.

    ```python
    print("Still keep internal code padding")
    ```

</div>

<details id="raw-padded-code" class="details-padded" open>
<summary>Raw padded code</summary>
<pre><code>Explicit inset</code></pre>
</details>

<details id="raw-padded-table" class="details-padded" open>
<summary>Raw padded table</summary>
<table><tr><th>Setting</th><th>Value</th></tr><tr><td>Inset</td><td>Padded</td></tr></table>
</details>

<details id="raw-flush-mixed" class="details-flush" open>
<summary>Raw flush mixed content</summary>
<p>Explicitly remove the surrounding inset.</p>
<pre><code>Still keep internal code padding</code></pre>
</details>

## Nested details and tabs

<div class="details-padded" markdown="1">

<details id="nested-outer" class="details-flush" open markdown="1">
<summary>Closest override wins</summary>

<details id="nested-inner" class="details-padded" open markdown="1">
<summary>Inner details override</summary>

```python
print("Inner details are padded")
```

</details>

<details id="nested-inherited" open>
<summary>Inherit the closest wrapper</summary>
<pre><code>Inherit flush from the outer details</code></pre>
</details>

=== "Independent tabs"

    ```python
    print("Tabs automatically select flush despite details overrides")
    ```

</details>

</div>

<details id="automatic-outer" open>
<summary>Automatic nested details</summary>
<details id="automatic-inner" open>
<summary>Inner code</summary>
<pre><code>Only the inner details automatically become flush.</code></pre>
</details>
</details>

<div id="details-in-tabs" class="tabs-flush" markdown="1">

=== "Independent details"

    ???+ note "Details still choose padded"

        A tab override does not change the details layout.

        ```text
        Mixed content stays padded.
        ```

</div>
