# Strategist

**File:** `src/planning/strategist.py`

The **"Brain"** of the agent. This is the LLM-powered reasoning node that receives the current page state and user goal, then decides what action to take next.

---

## `get_strategist_node()`

A factory function that returns the strategist node closure with the bound LLM.

```python
def get_strategist_node(bound_agent_tools: ChatOpenAI):
    def strategist_node(state: AgentState) -> Dict[Any, Any]:
        ...
    return strategist_node
```

---

## Node Logic

### Input Construction

The node builds the LLM prompt from the current state:

```python
user_message = f"""
## USER GOAL:
{state['user_goal']}
In order to complete the objective that the user asks of you, you have access
to a number of standard tools.
"""
```

### First Iteration vs. Subsequent

| Iteration | Messages Sent to LLM |
|---|---|
| **First** (`state["messages"]` is empty) | `[SystemMessage(SYSTEM_PROMPT), HumanMessage(user_message)]` |
| **Subsequent** | `state["messages"] + [HumanMessage("What you need to do next?")]` |

On the first call, the LLM receives the full system prompt + user goal. On subsequent calls, it receives the full conversation history plus a prompt asking what to do next.

### Output

```python
return {
    "messages": [response],          # The LLM's response (may contain tool calls)
    "previous_actions": ...,         # Last 10 actions kept
    "retry_count": 0,                # Reset retry counter
}
```

If the LLM invocation fails:

```python
return {
    "messages": [AIMessage(f"Strategist Error: {str(err)}")],
    "status": "failed",
}
```

---

## How the LLM Decides

The LLM has access to all tools defined in `toolnode.py`. It can:

1. **Call a tool** — Click, type, navigate, scroll, analyze screen, etc. → The router sends this to the Executor node.
2. **Return text** — If it determines the goal is complete or needs clarification → The router sends this to END.

The choice is encoded in the LLM's response format: if it includes `tool_calls`, the router routes to executor; otherwise, it routes to end.

---

## Streaming

The strategist node supports token-by-token streaming. In `main.py`, the streaming loop captures tokens from this node and displays them in real-time:

```python
if node_name == "strategist" and chunk.content:
    sys.stdout.write(chunk.content)  # Streams tokens as "🧠 THOUGHT:"
```

When tool calls are detected in the final message, they are logged separately:

```python
logger.info(f"⚡ ACTION: Using '{tool['name']}' with args: {tool['args']}")
```
