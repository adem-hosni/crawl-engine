# Workflow

**File:** `src/graph/workflow.py`

Defines the LangGraph `StateGraph` that orchestrates the entire agent loop.

---

## `build_graph()`

Assembles and compiles the LangGraph. Called by `src/main.py` at startup.

### Step-by-Step

```python
def build_graph():
```

**1. Create tools and bind to LLM**

```python
tools = agent_tools(llm=llm, summarization_llm=summarization_llm)
agent_llm = llm.bind_tools(tools)
```

- `agent_tools()` (from `toolnode.py`) collects all browser automation tools plus deepagents middleware tools (todo list, filesystem, sub-agents, summarization).
- `bind_tools()` makes the LLM aware of available tools so it can decide when to call them.

**2. Build the state graph**

```python
workflow = StateGraph(AgentState)
```

- Uses `AgentState` as the shared state schema.

**3. Register nodes**

```python
workflow.add_node("perception", perception_node)
workflow.add_node("strategist", get_strategist_node(agent_llm))
workflow.add_node("executor", ToolNode(tools))
```

| Node ID | Function | Description |
|---|---|---|
| `perception` | `perception_node` | Scans the page DOM and updates state |
| `strategist` | `get_strategist_node(agent_llm)` | LLM reasoning — decides next action |
| `executor` | `ToolNode(tools)` | Executes the chosen tool |

**4. Set entry point**

```python
workflow.set_entry_point("perception")
```

The agent always starts by perceiving the page.

**5. Define edges**

```python
workflow.add_edge("perception", "strategist")

workflow.add_conditional_edges(
    "strategist", router_node,
    {"executor": "executor", "end": END}
)

workflow.add_edge("executor", "perception")
```

| Edge | Type | Behavior |
|---|---|---|
| `perception → strategist` | Fixed | Always go from perception to strategist |
| `strategist → ?` | Conditional | If tool calls → `executor`; else → `END` |
| `executor → perception` | Fixed | Always loop back to re-scan the page |

**6. Compile**

```python
return workflow.compile()
```

---

## Graph Visualization

```
                    ┌──────────────┐
                    │  PERCEPTION  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  STRATEGIST  │
                    └──────┬───────┘
                           │
                     ┌─────▼──────┐
                     │  ROUTER    │
                     │(conditional)│
                     └─────┬──────┘
                      ┌────┴────┐
                      │         │
                      ▼         ▼
                ┌─────────┐  ┌─────┐
                │EXECUTOR │  │ END │
                └────┬────┘  └─────┘
                     │
                     └──→ PERCEPTION (loop)
```

---

## Streaming in `main.py`

The graph is streamed with two modes:

- **`"messages"`** — Streams individual token chunks from the strategist node (real-time thought display).
- **`"updates"`** — Streams complete node outputs (tool calls, tool results, perception updates).

The streaming loop in `main.py` reconstructs these into a coherent console output with icons:
- `🧠 THOUGHT:` — Strategist's reasoning tokens
- `⚡ ACTION:` — Tool calls with name and arguments
- `🛠️ TOOL OUTPUT:` — Tool execution results
- `👀 PERCEPTION:` — URL being scanned
