# Tool Node

**File:** `src/graph/toolnode.py`

Assembles the complete set of tools available to the agent LLM, combining core browser tools with [deepagents](https://pypi.org/project/deepagents/) middleware tools.

---

## `get_agent_tools()`

```python
def get_agent_tools(
    llm: ChatOpenAI,
    summarization_llm: ChatOpenAI,
    subagents: list[SubAgent | CompiledSubAgent] = [],
) -> List[Callable[..., Any]]:
```

### Core Browser Tools

These are always available. Defined in `src/execution/tools.py`:

| Tool | Description |
|---|---|
| `navigate_url` | Navigates the browser to a URL |
| `execute_javascript` | Executes raw JS in the browser |
| `read_page_sourcecode` | Returns simplified HTML of the current page |
| `ask_user_for_help` | Pauses and asks the user a question |
| `check_saved_knowledge` | Searches past Q&A in `agent_knowledge.json` |
| `refresh_page` | Refreshes the current page |
| `analyze_screen` | Captures screenshot and queries vision LLM |

### Deepagents Middleware Tools

Each middleware adds its own set of tools:

| Middleware | Tools Added | Purpose |
|---|---|---|
| `TodoListMiddleware` | Todo list CRUD tools | Enables the agent to maintain a task list |
| `FilesystemMiddleware` | File read/write/list tools | Allows the agent to read/write local files |
| `SubAgentMiddleware` | Sub-agent delegation tools | Lets the agent spawn sub-agents for subtasks |
| `PatchToolCallsMiddleware` | Tool call patching tools | Fixes malformed tool calls before execution |
| `SummarizationMiddleware` | Summarization tools | Compresses context via summarization |

### How Tools Are Combined

```python
AGENT_TOOLS = [navigate_url, execute_javascript, ..., analyze_screen]

return AGENT_TOOLS + [
    tool
    for middleware in [
        TodoListMiddleware(),
        FilesystemMiddleware(backend=backend),
        SubAgentMiddleware(default_model=llm, default_tools=AGENT_TOOLS, subagents=subagents),
        PatchToolCallsMiddleware(),
        SummarizationMiddleware(model=summarization_llm, backend=backend),
    ]
    for tool in getattr(middleware, "tools", [])
]
```

This flattens all middleware `.tools` properties into a single list alongside the core tools.

---

## Module-Level Helper

```python
agent_tools = lambda **kwargs: get_agent_tools(**kwargs)
```

A convenience lambda so `workflow.py` can call:

```python
tools = agent_tools(llm=llm, summarization_llm=summarization_llm)
```

---

## How Tools Flow Through the Graph

```
get_agent_tools()
       │
       ▼
agent_tools(llm=llm, summarization_llm=...)  →  List[Callable]
       │
       ▼
llm.bind_tools(tools)  →  LLM aware of all tools
       │
       ▼
ToolNode(tools)  →  Executor node invokes tool calls
```
