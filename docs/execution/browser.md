# Browser Manager

**File:** `src/execution/browser.py`

The **"Hands"** of the agent. Wraps SeleniumBase's undetected ChromeDriver with high-level automation methods.

---

## `BrowserManager`

```python
class BrowserManager:
    def __init__(self, vision_model):
        self.driver = Driver(
            browser="chrome",
            uc=True,                    # Undetected ChromeDriver
            headless=False,             # Visible browser window
            binary_location=r"C:\Program Files (x86)\chrome\chrome.exe",
            locale_code="en",
        )
        self.vision = VisionAnalyzer(vision_model)
        self.wait = WebDriverWait(self.driver, 1)
```

### Key Properties

| Property | Type | Description |
|---|---|---|
| `driver` | `seleniumbase.Driver` | The Selenium WebDriver instance |
| `vision` | `VisionAnalyzer` | Vision analysis module for screenshots |
| `wait` | `WebDriverWait` | Explicit wait with 1-second timeout |

---

## Methods

### `navigate_to(url: str)`

Navigates the browser to a URL.

```python
def navigate_to(self, url: str) -> None:
```

- Uses `driver.get(url)` with a 2-second hard wait after navigation.

### `get_visual_context(query: str)`

Captures a screenshot and analyzes it with the vision LLM.

```python
def get_visual_context(self, query: str = None) -> str:
```

- Default query: "Describe the current page layout, focusing on interactive elements..."
- Delegates to `self.vision.analyze_page()`.

### `click_element(selector, by_method)`

Smart clicking with automatic fallback.

```python
def click_element(self, selector: str, by_method: str = "id") -> str:
```

1. Finds element using explicit wait.
2. Scrolls it into view (`scrollIntoView` with `block: 'center'`).
3. Attempts standard Selenium `.click()`.
4. If `ElementClickInterceptedException` or `ElementNotInteractableException` → falls back to JavaScript `arguments[0].click()`.

Returns a status string describing which method was used.

### `insert_text(text, selector, by_method)`

Types text into an input field.

```python
def insert_text(self, text: str, selector: str, by_method: str = "id") -> str:
```

1. Finds and scrolls to the element.
2. Attempts to click it (may fail silently for some elements).
3. Clears the field with `.clear()`.
4. Sends the text with `.send_keys()`.
5. Presses Enter with `Keys.RETURN`.

### `get_compressed_dom()`

Extracts a token-efficient representation of the page.

```python
def get_compressed_dom(self):
```

1. Parses HTML with BeautifulSoup.
2. Removes `<script>`, `<style>`, `<svg>`, `<path>`, `<noscript>`.
3. Finds only interactive/heading tags: `a`, `button`, `input`, `textarea`, `select`, `h1`, `h2`, `p`.
4. Formats each as: `Tag: <a> | Text: Login | ID: login-btn | Class: btn primary`
5. Returns up to 150 elements.

**Note:** This method exists on the browser but is not used in the current graph. The `DOMCleaner` in `perception/dom_cleaner.py` handles the actual perception node logic.

### `_select_element(selector, by_method)`

Internal method for element lookup with explicit wait.

```python
def _select_element(self, selector: str, by_method: str = "id"):
```

- Converts `by_method` string to a Selenium `By` attribute (e.g., `"id"` → `By.ID`, `"xpath"` → `By.XPATH`).
- Waits up to 1 second for the element to be present.

---

## Module-Level Singletons

```python
browser = BrowserManager(vision_model)
driver = browser.driver
```

These singletons are imported directly by tools and nodes:

| Import | Used By |
|---|---|
| `from execution.browser import browser` | `tools.py` — all browser tool functions |
| `from execution.browser import driver` | `nodes.py` — perception node reads `driver.current_url` and `driver.page_source` |

---

## Chrome Binary Path

The browser manager has a hardcoded Chrome binary path:

```python
binary_location=r"C:\Program Files (x86)\chrome\chrome.exe"
```

If Chrome is installed elsewhere, update this path. The `uc=True` flag enables `undetected-chromedriver`, which patches ChromeDriver to avoid bot detection.
