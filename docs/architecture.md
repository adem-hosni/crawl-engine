# Architecture

The Crawl Engine is an **autonomous browser agent** orchestrated by a [LangGraph](https://langchain-ai.github.io/langgraph/) state machine. It follows a **perception → reasoning → execution → loop** pattern, where each cycle re-scans the page and decides the next action.

---

## High-Level Design

```
┌──────────────────────────────────────────────────────────┐
│                     LANGGRAPH                             │
│                                                          │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐    │
│   │ PERCEPTION │───►│ STRATEGIST │───►│ EXECUTOR   │    │
│   │   (Node)   │    │   (Node)   │    │   (Node)   │    │
│   └────────────┘    └─────┬──────┘    └──────┬─────┘    │
│         ▲                 │                   │          │
│         │           ┌─────▼──────┐            │          │
│         │           │   ROUTER   │            │          │
│         │           │ (Condition)│            │          │
│         │           │  /toolcall │            │          │
│         │           └─────┬──────┘            │          │
│         │                 │                   │          │
│         │            ┌────▼────┐              │          │
│         │            │   END   │              │          │
│         └────────────┴─────────┘◄─────────────┘          │
│                                                          │
│   ┌────────────┐    (conditional edge)                   │
│   │SUMMARIZER  │◄─── when messages > 6                   │
│   └────────────┘                                         │
└──────────────────────────────────────────────────────────┘
```

### Loop Flow

1. **Perception Node** — Scans the current browser page.
   - Extracts raw HTML from Selenium.
   - Parses it with BeautifulSoup to find interactive elements.
   - Assigns each element a numeric ID and generates an XPath.
   - Stores the clean DOM text and element map into state.

2. **Strategist Node** — The LLM reasoning hub.
   - Receives the user goal, clean DOM, and message history.
   - Decides the next action: click an element, type text, navigate, etc.
   - Returns either a tool call (→ Executor) or a text response (→ End).

3. **Router Node** — Conditional branching.
   - If the strategist produced tool calls → route to **Executor**.
   - Otherwise → route to **End**.

4. **Executor Node** — Executes the tool call using the browser.
   - Resolves element IDs to XPaths via `BrowserContext`.
   - Performs the actual Selenium interaction.
   - Returns the result message.

5. **Summarizer Node** — (Triggered when messages > 6)
   - Compresses older conversation history into a summary.
   - Removes summarized messages to keep context lean.

---

## Data Flow

```
User Goal (string)
       │
       ▼
┌─────────────────────────────────────────────────────┐
│                  AGENT STATE                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │ messages │ │ user_goal│ │ clean_dom        │    │
│  │ (list)   │ │ (string) │ │ (string)         │    │
│  ├──────────┤ ├──────────┤ ├──────────────────┤    │
│  │ summary  │ │ todo_list│ │ interactive_elem │    │
│  │ (string) │ │ (list)   │ │ (dict ID→XPath)  │    │
│  └──────────┘ └──────────┘ └──────────────────┘    │
└─────────────────────────────────────────────────────┘
```

- **`messages`** — Accumulates all LLM interactions and tool results (LangGraph's `add_messages` reducer appends new messages).
- **`clean_dom`** — Updated by the perception node each cycle.
- **`interactive_elements`** — A dict mapping numeric IDs to XPath strings, consumed by the execution tools.
- **`summary`** — Holds the compressed conversation summary from the summarizer node.

---

## Component Dependencies

```
src/main.py
  ├── src/graph/workflow.py
  │     ├── src/graph/nodes.py
  │     │     ├── src/perception/dom_cleaner.py
  │     │     ├── src/execution/browser.py
  │     │     └── src/execution/context.py
  │     ├── src/graph/toolnode.py
  │     │     └── src/execution/tools.py
  │     ├── src/planning/strategist.py
  │     │     └── src/core/prompts.py
  │     └── src/core/llms.py
  │           ├── src/core/callbacks.py
  │           ├── langchain_openai
  │           └── langchain_anthropic
  └── src/config/logger.py
        └── rich
```

- **No circular dependencies** — The graph has a clean layered structure.
- **Main** imports and assembles everything.
- **Tools** depend on `browser.py` and `context.py`.
- **Nodes** depend on `perception/`, `execution/`, and `core/`.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **LangGraph over direct loop** | State machine provides checkpoints, streaming, and conditional routing out of the box. |
| **OpenRouter over local models** | Access to many models (DeepSeek, Claude, Qwen, Gemma) via a single API. |
| **Numeric element IDs** | LLMs handle numbers better than raw XPaths. The `BrowserContext` singleton resolves IDs transparently. |
| **Vision as a tool** | The LLM can call `analyze_screen` when it needs visual context, rather than sending screenshots every cycle. |
| **Deepagents middleware** | Provides todo lists, filesystem operations, sub-agents, and summarization as composable middleware layers. |
