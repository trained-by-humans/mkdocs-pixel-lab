# Code highlighting

Keywords, strings, functions, and comments use the theme palette. The marked
lines are emphasized without changing the copied code.

```{ .python hl_lines="4-5" }
import math

def greet(name):
    # Return a greeting.
    return "Hello, " + name
print(greet("Pixel Lab"))
```

```json
{"enabled": true, "name": "Pixel Lab"}
```

## Sibling block alignment

<div id="block-alignment" markdown="1">

??? note "Toggle the aligned details"

    ```text
    Nested code remains flat inside the details frame.
    ```

```text
A long code line should scroll inside its frame without changing the alignment of the surrounding sibling blocks.
```

!!! note "Aligned admonition"

    ???+ tip "Nested details"

        Nested details remain flat inside the admonition frame.

</div>
