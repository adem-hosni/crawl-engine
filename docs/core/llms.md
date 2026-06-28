# LLM Models

**File:** `src/core/llms.py`

Initializes the three language models used by the agent, all routed through [OpenRouter](https://openrouter.ai/).

---

## Overview

The system uses three distinct LLMs with different roles:

| Model | Variable | Default | Purpose |
|---|---|---|---|
| **Agent LLM** | `agent_llm` | `deepseek/deepseek-v3.2` | Strategic reasoning & decision-making |
| **Vision Model** | `vision_model` | `qwen/qwen2.5-vl-32b-instruct` | Screenshot analysis |
| **Summarization LLM** | `summarization_llm` | `google/gemma-3-12b-it` | Conversation compression |

---

## Functions

### `_get_agent_llm()`

Creates the primary reasoning model.

- Supports Claude models via `ChatAnthropic` (if model name contains `"claude"`).
- Falls back to `ChatOpenAI` with the OpenRouter base URL for all other models.
- Configured with `temperature=0` for deterministic behavior.
- Enables `streaming=True` for real-time token output.

```python
# Example: using DeepSeek via OpenRouter
return ChatOpenAI(
    model="deepseek/deepseek-v3.2",
    temperature=0,
    openai_api_key="sk-or-v1-...",
    openai_api_base="https://openrouter.ai/api/v1",
    streaming=True,
)
```

### `_get_vision_model()`

Creates the vision-capable model for screenshot analysis.

- Same OpenRouter `ChatOpenAI` setup as the agent model.
- Adds `max_tokens=1000` to cap response length (vision responses can be verbose).
- Does **not** use streaming (full response needed for analysis).

### `_get_summarization_llm()`

Creates the model for conversation summarization.

- Same OpenRouter `ChatOpenAI` setup.
- Attaches `SummaryCaptureHandler` callback to log summary outputs.
- Configured with `temperature=0` for consistent summaries.

---

## Module-Level Singletons

At module import time, three singletons are created:

```python
agent_llm = _get_agent_llm()
summarization_llm = _get_summarization_llm()
vision_model = _get_vision_model()
```

These are used throughout the codebase:
- `agent_llm` → `workflow.py`, `strategist.py`, `toolnode.py`
- `vision_model` → `browser.py`
- `summarization_llm` → `nodes.py`, `toolnode.py`

---

## Configuration

All model choices are driven by environment variables (see `.env`):

```
LLM_MODEL=deepseek/deepseek-v3.2
VISION_MODEL=qwen/qwen2.5-vl-32b-instruct
SUMMARIZATION_LLM=google/gemma-3-12b-it
```

Any model available on [OpenRouter](https://openrouter.ai/models) can be used. Common alternatives:

| Role | Alternative Models |
|---|---|
| Agent | `anthropic/claude-3.5-sonnet`, `google/gemini-2.0-flash`, `openai/gpt-4o` |
| Vision | `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`, `google/gemini-2.0-flash` |
| Summarization | `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`, `mistral/mistral-small` |
