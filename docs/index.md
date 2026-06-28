# Crawl Engine

An **LLM-powered autonomous browser agent** built with [LangGraph](https://langchain-ai.github.io/langgraph/) and [SeleniumBase](https://seleniumbase.io/). The agent perceives web pages, plans actions using an LLM, and executes browser interactions in a continuous loop — all through OpenRouter API.

---

## Features

- **Autonomous Browsing** — Navigates, clicks, types, scrolls, and reads web pages without human intervention.
- **LLM-Driven Reasoning** — Uses a configurable agent LLM (e.g., DeepSeek, Claude) via OpenRouter for strategic decision-making.
- **Vision Analysis** — Captures screenshots and queries a vision-capable LLM for visual context.
- **DOM Perception** — Parses live HTML into structured, numbered interactive elements with XPath resolution.
- **Conversation Memory** — Summarizes old messages to stay within context windows.
- **Persistent Knowledge** — Saves Q&A interactions to a local JSON file for cross-session recall.
- **Rich Logging** — Colored console output via Rich + rotating file logs for debugging.
- **Smart Click Fallback** — Uses standard clicks first, then JavaScript forced clicks when intercepted.

---

## Repository Structure

```
crawl-engine/
├── src/
│   ├── main.py                 # Entry point — builds & runs the LangGraph
│   ├── config/
│   │   └── logger.py           # Logging configuration (Rich + file)
│   ├── core/
│   │   ├── callbacks.py        # LLM callback handlers
│   │   ├── llms.py             # LLM model initialization (OpenRouter)
│   │   ├── prompts.py          # System prompts for the agent
│   │   └── state.py            # Agent state TypedDict
│   ├── execution/
│   │   ├── browser.py          # BrowserManager — SeleniumBase wrapper
│   │   ├── context.py          # BrowserContext — element ID→XPath mapping
│   │   └── tools.py            # LangChain tools for browser automation
│   ├── graph/
│   │   ├── nodes.py            # Perception, router, summarization nodes
│   │   ├── toolnode.py         # Tool node with deepagents middleware
│   │   └── workflow.py         # LangGraph StateGraph definition
│   ├── perception/
│   │   ├── dom_cleaner.py      # DOM parsing & element mapping
│   │   └── vision.py           # Screenshot + vision LLM analysis
│   └── planning/
│       └── strategist.py       # Main LLM reasoning node
├── docs/                       # Full documentation (this folder)
├── .env.example                # Environment variables template
├── pyproject.toml              # Project metadata & dependencies
├── langgraph.json              # LangGraph platform config
└── agent_knowledge.json        # Persistent Q&A knowledge store
```

---

## How It Works

The system runs as a **perception → reasoning → execution → loop**:

```
┌──────────────┐
│  PERCEPTION  │  Scan page, parse DOM, capture screenshot
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  STRATEGIST  │  LLM decides next action (tool call or done)
└──────┬───────┘
       │
  ┌────┴────┐
  │         │
  ▼         ▼
EXECUTOR   END
  │
  └──→ back to PERCEPTION
```

1. **Perception Node** — Reads the current page HTML, extracts interactive elements (buttons, inputs, links), assigns each a numeric ID, and captures a screenshot for vision analysis.
2. **Strategist Node** — The LLM receives the user goal + current page state and decides the next action (click an element, type text, navigate to a URL, or ask the user for help).
3. **Executor Node** — Executes the tool call returned by the LLM (click, type, navigate, scroll, JS execution, etc.).
4. **Loop** — After execution, the cycle repeats: re-scan the page, re-decide, until the goal is complete.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/crawl-engine.git
cd crawl-engine

# Install dependencies
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your OpenRouter API key

# Run the agent
python src/main.py
```

> **Prerequisites:** Python 3.13+, Google Chrome installed, and an [OpenRouter](https://openrouter.ai/) API key.

---

## Configuration

All configuration is done via environment variables (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | Your OpenRouter API key |
| `LLM_MODEL` | `deepseek/deepseek-v3.2` | Model for agent reasoning |
| `VISION_MODEL` | `qwen/qwen2.5-vl-32b-instruct` | Model for visual analysis |
| `SUMMARIZATION_LLM` | `google/gemma-3-12b-it` | Model for conversation summarization |

---

## Documentation Index

| Module | File | Description |
|---|---|---|
| [Configuration & Logging](config/logger.md) | `src/config/logger.py` | Rich console + rotating file logger |
| [LLM Models](core/llms.md) | `src/core/llms.py` | Agent, vision, and summarization LLM setup |
| [Prompts](core/prompts.md) | `src/core/prompts.py` | System prompts for the agent |
| [State](core/state.md) | `src/core/state.py` | Agent state TypedDict |
| [Callbacks](core/callbacks.md) | `src/core/callbacks.py` | LLM callback handlers |
| [Workflow](graph/workflow.md) | `src/graph/workflow.py` | LangGraph StateGraph definition |
| [Nodes](graph/nodes.md) | `src/graph/nodes.py` | Graph nodes (perception, router, summarizer) |
| [Tool Node](graph/toolnode.md) | `src/graph/toolnode.py` | Tool assembly with deepagents middleware |
| [Strategist](planning/strategist.md) | `src/planning/strategist.py` | Main LLM reasoning node |
| [Browser Manager](execution/browser.md) | `src/execution/browser.py` | SeleniumBase browser wrapper |
| [Execution Context](execution/context.md) | `src/execution/context.py` | Element ID→XPath singleton |
| [Browser Tools](execution/tools.md) | `src/execution/tools.py` | All browser automation tools |
| [DOM Cleaner](perception/dom_cleaner.md) | `src/perception/dom_cleaner.py` | HTML parsing & element mapping |
| [Vision Analyzer](perception/vision.md) | `src/perception/vision.py` | Screenshot + vision LLM |
| [Entry Point](getting-started.md) | `src/main.py` | Application entry point & streaming loop |
