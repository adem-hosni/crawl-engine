# DOM Cleaner

**File:** `src/perception/dom_cleaner.py`

The **"Eyes"** of the agent. Transforms raw browser HTML into a structured, numbered list of interactive elements that the LLM can understand and reference.

---

## `DOMCleaner`

```python
class DOMCleaner:
    def __init__(self):
        self.element_map = {}     # {numeric_id: xpath_string}
        self.counter = 0          # Auto-incrementing ID
```

---

## `clean_and_map(raw_html)`

The main entry point. Called by the perception node each cycle.

```python
def clean_and_map(self, raw_html: str) -> str:
```

### Process

1. **Parse** — Feed raw HTML to BeautifulSoup.
2. **Strip non-interactive tags** — Remove `<script>`, `<style>`, `<svg>`, `<path>`, `<footer>`, `<meta>`, `<link>`, `<noscript>`.
3. **Find interactive elements** — Search for: `a`, `button`, `input`, `textarea`, `select`, `h1`–`h6`, `p`, `pre`.
4. **Assign IDs** — Each element gets a sequential numeric ID starting from 0.
5. **Generate descriptions** — Call `_describe_element()` for a human-readable label.
6. **Generate XPaths** — Call `_get_xpath()` and store in `self.element_map`.

### Output Format

```
[0] Button: Sign In
[1] Input (email): Email address
[2] Input (password): Password
[3] Link: Forgot password?
[4] Button: Submit
```

This clean text is stored as `state["clean_dom"]` and presented to the LLM.

---

## `_describe_element(tag)`

Generates a human-readable description for each element based on its HTML tag and attributes.

| Tag | Description Format | Example |
|---|---|---|
| `<a>` | `Link: {text/aria/href}` | `Link: Sign In` |
| `<input type="submit">` | `Button: {value/aria}` | `Button: Submit` |
| `<input type="text">` | `Input (text): {placeholder/aria}` | `Input (text): Email address` |
| `<input type="checkbox">` | `Checkbox (checked/unchecked): {aria/name}` | `Checkbox (unchecked): Remember me` |
| `<input type="radio">` | `Radio (checked/unchecked): {aria/name}` | `Radio (unchecked): Option 1` |
| `<button>` | `Button: {text/aria}` | `Button: Create Account` |
| `<select>` | `Dropdown: {aria/name}` | `Dropdown: Country` |
| `<textarea>` | `Text Area: {placeholder/aria}` | `Text Area: Your message` |
| `<h1>`–`<h6>` | `Heading (h1): {text}` | `Heading (h1): Welcome` |
| `<p>` | `Paragraph: {text}` | `Paragraph: Enter your details below` |
| `<label>` | `Label: {text}` | `Label: Full Name` |

For any unrecognized tag, falls back to `{tag_name}: {text/aria}`.

The `pick()` helper selects the first non-empty string from a list of candidates.

---

## `_get_xpath(element)`

Generates a stable XPath selector for a BeautifulSoup tag, prioritizing:

1. **ID** → `//div[@id='main-content']`
2. **Name** → `//input[@name='email']`
3. **Class** → `//button[@class='btn primary']`
4. **Text** → `//button[text()='Sign In']`
5. **Fallback** → `//div` (bare tag name)

---

## `_is_visible(tag)`

Quick visibility check:

```python
def _is_visible(self, tag: Tag) -> bool:
    if tag.has_attr("hidden") or tag.get("type") == "hidden":
        return False
    return True
```

Currently, the perception node bypasses this check (always sets elements as visible), but the method is available for future filtering.

---

## Element Map

The `element_map` dictionary is consumed by the perception node:

```python
# In nodes.py:
cleaner = DOMCleaner()
clean_text = cleaner.clean_and_map(raw_html)
BrowserContext.set_map(cleaner.element_map)

return {
    "clean_dom": clean_text,
    "interactive_elements": cleaner.element_map,
    ...
}
```

Each tool function later resolves IDs through `BrowserContext.get_selector(id)`.
