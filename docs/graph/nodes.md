# Nodes

**File:** `src/graph/nodes.py`

Contains the three primary graph nodes and the summarization node.

---

## `perception_node()`

The **"Eyes"** of the agent. Runs every cycle to re-scan the current browser page.

```python
def perception_node(state: AgentState):
```

### What it does

1. Checks if the browser has a current URL. If not (e.g., no page loaded), returns empty DOM.
2. Gets `driver.page_source` — the full raw HTML of the current page.
3. Calls `DOMCleaner.clean_and_map(raw_html)` to:
   - Parse HTML with BeautifulSoup.
   - Remove non-interactive tags (scripts, styles, SVGs, etc.).
   - Assign each interactive element a unique numeric ID.
   - Generate an XPath selector for each element.
4. Stores the element map in `BrowserContext` (the singleton that tools use to resolve IDs).

### Returns

```python
{
    "clean_dom": str,                # Numbered list of interactive elements
    "current_url": str,              # The browser's current URL
    "interactive_elements": dict,    # {id: xpath_string}
}
```

---

## `router_node()`

The **"Traffic Controller"**. Decides whether to execute a tool or end the loop.

```python
def router_node(state: AgentState):
```

### Logic

- If the last message in state contains tool calls → route to `"executor"`.
- Otherwise → route to `"end"` (the graph terminates).

This is used as a conditional edge function in the workflow:

```python
workflow.add_conditional_edges(
    "strategist", router_node,
    {"executor": "executor", "end": END}
)
```

---

## `summarization_node()`

The **"Memory Manager"**. Prevents the conversation context from growing unboundedly.

```python
def summarization_node(state: AgentState):
```

### When it runs

Triggered by `should_summarize_route()` when `len(messages) > 6`.

### What it does

1. Reads the current summary (or "No previous summary exists.").
2. Takes all messages **except the last 7**.
3. Builds a prompt combining the current summary + new conversation lines.
4. Calls the summarization LLM with `SUMMARIZATION_SYSTEMPROMPT`.
5. Returns the new summary and `RemoveMessage` entries for the old messages.

### Returns

```python
{
    "summary": str,                          # Updated compressed summary
    "messages": [RemoveMessage(id=...), ...] # LangGraph removes these
}
```

---

## `should_summarize_route()`

A conditional edge function that runs before looping from the executor back to perception.

```python
def should_summarize_route(state: AgentState):
    if len(state["messages"]) > 6:
        return "summarizer"
    return "perception"
```

This is currently **defined but not wired into the workflow**. The summarization node is ready to be added as an intermediate step between executor and perception when needed.
