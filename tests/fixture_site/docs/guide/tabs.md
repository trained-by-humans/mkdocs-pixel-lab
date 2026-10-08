# Tab layouts

## Automatic layout

<div id="automatic-tabs" markdown="1">

=== "Code"

    ```python
    print("A code-only tab fills its panel without an extra surrounding frame or gap.")
    ```

=== "Table"

    | Payload | Preview |
    | --- | --- |
    | `a_very_long_unbroken_payload_name_to_exercise_horizontal_scrolling_in_a_narrow_tab_panel` | ![Preview](../assets/pixel-lab-preview.svg) |

=== "Mixed"

    Prose still needs a comfortable inset.

    ```python
    print("Code with an introduction stays padded")
    ```

=== "Multiple blocks"

    ```python
    print("First")
    ```

    ```python
    print("Second")
    ```

</div>

## Forced padding

<div id="padded-tabs" class="tabs-padded" markdown="1">

=== "Code"

    ```python
    print("Padding is explicitly requested")
    ```

</div>

## Forced flush

<div class="tabs-padded" markdown="1">
<div id="flush-tabs" class="tabs-flush" markdown="1">

=== "Mixed"

    This mixed-content panel explicitly opts out of the inset.

    ```python
    print("The closest wrapper wins")
    ```

</div>
</div>

## Nested tabs

<div id="nested-tabs" markdown="1">

=== "Outer"

    === "Inner code"

        ```python
        print("The inner panel is flush; the outer panel is padded")
        ```

</div>
