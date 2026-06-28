# Browser Tools

**File:** `src/execution/tools.py`

All LangChain tools that the agent LLM can call to interact with the browser, the user, and local storage.

---

## Element Resolution

Tools that accept `element_id: int` use a shared helper to convert numeric IDs to XPath selectors:

```python
def _resolve_selector(element_id: int) -> str:
    xpath = BrowserContext.get_selector(element_id)
    if not xpath:
        raise ValueError(f"Element ID [{element_id}] is invalid or not in the current view.")
    return xpath
```

The element map is populated each cycle by the perception node and stored in the `BrowserContext` singleton.

---

## Tool Reference

### `navigate_url(url: str)`

Navigates the browser to a URL.

```python
@tool(description="Navigates the browser to a specific URL. Example: navigate_url(url='https://google.com')")
def navigate_url(url: str):
```

- Calls `browser.navigate_to(url)`.
- Returns `"Navigated to {url}"` on success.

### `click_element(element_id: int)`

Clicks an interactive element by its numeric ID.

```python
@tool(description="Clicks on an interactive element identified by its numeric ID [x].")
def click_element(element_id: int):
```

- Resolves the ID to an XPath.
- Calls `browser.click_element()` with smart click + JS fallback.

### `insert_text(element_id: int, text: str)`

Types text into an input field identified by its numeric ID.

```python
@tool(description="Types text into an input field identified by its numeric ID [x].")
def insert_text(element_id: int, text: str):
```

- Resolves the ID to an XPath.
- Calls `browser.insert_text()` which clears the field, types the text, and presses Enter.

### `scroll_element(element_id: int)`

Scrolls the page until an element is visible.

```python
@tool
def scroll_element(element_id: int):
```

- Resolves the ID, scrolls into view with smooth behavior.
- Returns `"Scrolled to element [{id}]"`.

### `analyze_screen(query: str)`

Captures a screenshot and analyzes it with the vision LLM.

```python
@tool
def analyze_screen(query: str):
```

- Delegates to `browser.get_visual_context(query)`.
- Useful when the DOM alone doesn't give enough context (e.g., popups, errors, CAPTCHAs).

### `execute_javascript(code: str)`

Executes raw JavaScript in the browser context.

```python
@tool(description="Executes raw JavaScript code with no comments in the browser.")
def execute_javascript(code: str) -> str:
```

- Use as a **last resort** when standard click/type tools fail.
- Returns the JS return value or a success message.

### `read_page_sourcecode()`

Returns a cleaned, minified HTML representation of the current page.

```python
@tool(description="Scans the current page and returns a simplified, clean HTML representation.")
def read_page_sourcecode():
```

- Parses with BeautifulSoup.
- Removes scripts, styles, SVGs, footers, meta tags, and comments.
- Strips non-essential attributes (`style`, `class`, `data-*`, `aria-*`, etc.).
- Collapses redundant nested `<div>` and `<span>` tags.

### `refresh_page(wait_time: int = 3)`

Refreshes the current page.

```python
@tool
def refresh_page(wait_time: int = 3):
```

- Refreshes and waits `wait_time` seconds.

### `ask_user_for_help(question: str)`

Pauses execution and asks the human user a question via console input.

```python
@tool(description="Use this ONLY when stuck, confused, or need a login code/password.")
def ask_user_for_help(question: str) -> str:
```

1. Prints the question to the console.
2. Reads the user's answer from stdin.
3. Saves the Q&A pair to `agent_knowledge.json` via `_save_knowledge()`.
4. Returns the answer so the LLM can proceed.

### `check_saved_knowledge(query: str)`

Searches past Q&A interactions in `agent_knowledge.json`.

```python
@tool
def check_saved_knowledge(query: str) -> str:
```

- Loads the knowledge file.
- Finds entries where any query word matches the stored question.
- Returns matching Q&A pairs or a "not found" message.

---

## Knowledge Persistence

The `_save_knowledge()` helper appends Q&A entries to `agent_knowledge.json`:

```python
KNOWLEDGE_FILE = "agent_knowledge.json"

def _save_knowledge(question: str, answer: str):
```

Each entry has:

```json
{
    "timestamp": "2026-02-04 19:38:49",
    "question": "What is your email?",
    "answer": "user@example.com"
}
```

This enables cross-session memory — the agent can recall information the user provided in previous runs.
