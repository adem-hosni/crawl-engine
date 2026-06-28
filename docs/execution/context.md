# Execution Context

**File:** `src/execution/context.py`

A minimal singleton that holds the mapping between numeric element IDs and their XPath selectors during a single perception-execution cycle.

---

## `BrowserContext`

```python
class BrowserContext:
    _element_map = {}
```

### Why It Exists

The `DOMCleaner` assigns each interactive element on the page a numeric ID (e.g., `[0]`, `[1]`, `[12]`). When the LLM decides to click element `[5]`, the tool needs to resolve `5` to an actual XPath like `//button[@id="submit"]`.

Rather than passing the full dictionary through function arguments or state, `BrowserContext` acts as a **thread-safe singleton** that both the perception node (writer) and tool functions (readers) can access.

### Methods

#### `set_map(new_map: dict)`

Called by the perception node after DOM cleaning:

```python
BrowserContext.set_map(cleaner.element_map)
```

#### `get_selector(element_id: int) -> str`

Called by tool functions to resolve an ID:

```python
xpath = BrowserContext.get_selector(5)
# Returns: "//button[@id='submit']"
```

Returns `None` if the ID is not in the current map.

---

## Lifecycle

```
PERCEPTION NODE
   │
   ├── DOMCleaner.clean_and_map(html) → element_map = {0: "//...", 1: "//...", ...}
   │
   └── BrowserContext.set_map(element_map)    ← WRITE
                              │
                              ▼
                         (between nodes)
                              │
                              ▼
TOOL FUNCTION (e.g., click_element)
   │
   └── BrowserContext.get_selector(element_id) → xpath  ← READ
```

The map is overwritten every perception cycle, so stale selectors from a previous page are automatically discarded.
