# Vision Analyzer

**File:** `src/perception/vision.py`

Provides visual context by capturing browser screenshots and querying a vision-capable LLM.

---

## `VisionAnalyzer`

```python
class VisionAnalyzer:
    def __init__(self, model: ChatOpenAI):
        self.model = model
```

Takes a `ChatOpenAI` vision model (configured in `src/core/llms.py` via `_get_vision_model()`).

---

## `analyze_page(driver, prompt)`

The core method — captures what the browser sees and asks the vision model to interpret it.

```python
def analyze_page(self, driver: Chrome, prompt: str) -> str:
```

### Process

1. **Capture Screenshot** — `driver.get_screenshot_as_base64()` returns the current viewport as a base64-encoded PNG.
2. **Build Multimodal Message** — Creates a `HumanMessage` with both text and image:
   ```python
   message = HumanMessage(content=[
       {"type": "text", "text": prompt},
       {"type": "image_url", "image_url": {
           "url": f"data:image/png;base64,{screenshot_b64}"
       }},
   ])
   ```
3. **Invoke Vision Model** — Sends the message to the configured vision LLM.
4. **Return Analysis** — Returns the model's text response describing the page.

### Error Handling

If the API call fails (e.g., rate limit, invalid image), it logs the error and returns a fallback message:

```python
return f"Error: Unable to analyze the visual content."
```

---

## Usage Flow

The `analyze_screen` tool (in `tools.py`) calls the vision analyzer:

```python
@tool
def analyze_screen(query: str):
    return browser.get_visual_context(query)
```

Which in turn calls:

```python
# browser.py
def get_visual_context(self, query: str = None) -> str:
    prompt = query or "Describe the current page layout..."
    return self.vision.analyze_page(self.driver, prompt)
```

---

## When to Use

Vision analysis is **complementary** to DOM parsing:

| Scenario | DOM | Vision |
|---|---|---|
| Normal form filling | ✅ Precise element IDs | ❌ Not needed |
| CAPTCHA or popup detection | ❌ Hidden from DOM | ✅ Can detect visually |
| Page layout validation | ❌ Only sees structure | ✅ Sees actual rendering |
| Error messages in overlays | ❌ May be hidden | ✅ Always visible |

The LLM decides when to call `analyze_screen` based on whether it needs visual information.
