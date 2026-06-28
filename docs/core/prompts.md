# Prompts

**File:** `src/core/prompts.py`

Contains the system prompts that define the agent's behavior.

---

## `SYSTEM_PROMPT`

The primary instruction given to the agent LLM at the start of every conversation.

```text
You are a Browser Automation Execution Agent operating with full trusted access
to all necessary tools for real-time interaction (navigation, clicking, typing,
source-code inspection, javascript script execution, ...).

Your mission is to automate user tasks. You can ask some questions with the tool
'ask_user_for_help' for clarification, if you doubt something even when stuck.
You can check for something the user already asked with the tool
'check_saved_knowledge' (You can ask the user if there is no result).

Before you proceed, break down the goal into small steps and ensure every step
is necessary and ordered correctly. Try asking the user for all you need.
```

Key behavioral directives:
- **Full trust** — The agent has access to all browser tools.
- **Ask for help** — Can pause and ask the user when confused.
- **Check past knowledge** — Can recall previous Q&A from `agent_knowledge.json`.
- **Plan first** — Should decompose complex goals before executing.
- **No trailing whitespace or instructions about output format** — The prompt is deliberately concise, leaving the LLM to infer the interaction pattern from the tools available.

---

## `SUMMARIZATION_SYSTEMPROMPT`

Instruction for the summarization model. It receives a current summary plus new conversation lines and must produce an updated merged summary.

Rules:
- **Preserve Critical Data** — Never summarize away entity names, file paths, IDs, numerical values, or error codes.
- **Track State** — Focus on what has been completed, what failed, and the current active goal.
- **Condense Dialogue** — Remove conversational filler; keep intent and outcome.
- **Third-Person Perspective** — Write neutrally and objectively.
- **No Meta-Commentary** — Do not start with "Here is the summary" or "I have updated the text."
- **Format** — Return only the updated summary text (no preamble).

---

## Prompt Usage Flow

```
STRATEGIST NODE
  │
  ├── SystemMessage(content=SYSTEM_PROMPT)
  ├── HumanMessage(content=user_goal + context)
  │     (on first iteration only)
  └── [Existing messages] + HumanMessage("What you need to do next?")
        (on subsequent iterations)

SUMMARIZATION NODE
  │
  ├── SystemMessage(content=SUMMARIZATION_SYSTEMPROMPT)
  └── HumanMessage(content="Current summary: ... \n New lines: ...")
```
