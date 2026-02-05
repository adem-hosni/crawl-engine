"""Define the state structures for the agent."""

from __future__ import annotations

from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[list, add_messages]

    user_goal: str

    current_url: str
    clean_dom: str
    interactive_elements: Dict[int, Any]  # Map ID -> XPath/Selector

    # --- Plan
    todo_list: List[str]
    previous_actions: List[str]

    # --- Control
    last_action: Dict
    retry_count: int
    status: str
