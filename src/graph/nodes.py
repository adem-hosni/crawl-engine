from langgraph.prebuilt import ToolNode

from core.state import AgentState
from planning.strategist import strategist_node
from perception.dom_cleaner import DOMCleaner
from execution.tools import TOOLS
from execution.browser import driver
from execution.context import BrowserContext


cleaner = DOMCleaner()


def perception_node(state: AgentState):
    """Step 1: Look (Perception Module)"""

    print("--- PERCEPTION: LOOKING ---")
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


executor_node = ToolNode(TOOLS)


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
