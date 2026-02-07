from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

from core.state import AgentState
from core.llms import get_summarization_llm
from core.prompts import SUMMARIZATION_SYSTEMPROMPT

from perception.dom_cleaner import DOMCleaner

from execution.browser import driver
from execution.context import BrowserContext


cleaner = DOMCleaner()


def perception_node(state: AgentState):
    """Step 1: Look (Perception Module)"""

    if not driver.current_url:
        return {"clean_dom": "Empty", "current_url": "None"}

    raw_html = driver.page_source
    clean_text = cleaner.clean_and_map(raw_html)

    BrowserContext.set_map(cleaner.element_map)
    return {
        "clean_dom": clean_text,
        "current_url": driver.current_url,
        "interactive_elements": cleaner.element_map,
    }


def router_node(state: AgentState):
    """Step 4: Route (Traffic Control)"""
    messages = state["messages"]

    if not messages:
        print("--- 🛑 ERROR: Strategist returned no messages. Stopping. ---")
        return "end"

    last_message = messages[-1]

    # If the LLM called a tool, go to Executor
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "executor"
    return "end"


summarization_llm = get_summarization_llm()


def summarization_node(state: AgentState):
    """Summarizes older messages and removes them from history."""
    current_summary = state.get("summary", "No previous summary exists.")
    messages = state["messages"]

    # Keep the last 5 messages (Active Context) so Perception can see the Executor's activity
    # Summarizer everything else
    if len(messages) <= 7:
        return {"messages": []}

    messages_to_summarize = messages[:-7]

    prompt = f"""
Current summary: {current_summary}
New conversation lines: {"\n\n".join([message.content for message in messages_to_summarize])}
""".strip()

    response = summarization_llm.invoke(
        [
            SystemMessage(content=SUMMARIZATION_SYSTEMPROMPT),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "summary": response.content,
        "messages": [RemoveMessage(id=m.id) for m in messages_to_summarize],
    }


def should_summarize_route(state: AgentState):
    """Decides if we need to clean up before looping back."""
    if len(state["messages"]) > 6:
        return "summarizer"
    return "perception"
