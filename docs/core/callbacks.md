# Callbacks

**File:** `src/core/callbacks.py`

Contains LangChain callback handlers that hook into LLM lifecycle events.

---

## `SummaryCaptureHandler`

A `BaseCallbackHandler` that captures and logs the output of the summarization LLM.

### `on_llm_start()`

Triggered when the summarization LLM begins processing.

```python
def on_llm_start(self, serialized, prompts, *,
                 run_id, parent_run_id=None, tags=None, metadata=None, **kwargs):
```

- Logs: `"Summarization triggered on {len} chars..."` with the character count of the input prompt.

### `on_llm_end()`

Triggered when the summarization LLM finishes.

```python
def on_llm_end(self, response: LLMResult, *,
               run_id, parent_run_id=None, **kwargs):
```

- Extracts the generated text from the first generation.
- Logs: `"[SUMMARY]: {text[:130]}..."` (truncated to 130 characters for readability).
- Catches exceptions silently if the response format is unexpected.

---

## Usage

The handler is attached to the summarization LLM in `src/core/llms.py`:

```python
summarization_llm = ChatOpenAI(
    ...
    callbacks=[SummaryCaptureHandler()],
)
```

This means every call to the summarization model is automatically logged with both start and end events, providing visibility into memory compression without adding noise to the agent's primary reasoning logs.
