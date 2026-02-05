from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.base import BaseMessage

from core.state import AgentState
from core.prompts import SYSTEM_PROMPT
from core.llm import get_agent_llm


from execution.tools import TOOLS


class AgentDecision(BaseModel):
    action: str = Field(..., description="What you are doing and why")
    summary: str = Field(..., description="Action summary")


llm = get_agent_llm(TOOLS)


def strategist_node(state: AgentState) -> Dict[Any, Any]:
    """
    The Main Logic Node.
    Args:
        state: The current AgentState (dict)
    """
    user_goal = state["user_goal"]
    clean_dom = state.get("clean_dom", "No interactive elements.")
    current_url = state.get("current_url", "Unknown")
    messages: List[BaseMessage] = state.get("messages", [])
    previous_actions = state.get("previous_actions", [])

    evaluator_feedback = "No feedback yet."
    if messages and isinstance(messages[-1], SystemMessage):
        evaluator_feedback = messages[-1].content

    current_context = state.get("clean_dom", "No DOM detected.")

    # We grab the last few logs to give the agent "short-term memory"
    # recent_history = "\n - ".join(previous_actions[-10:])
    recent_history = "\n".join(msg.content for msg in messages[-10:])

    user_message = f"""
## USER GOAL:
{state['user_goal']}

## Previous Actions:
{recent_history}

## Current Browser STATE (Interactive Elements):
{current_context}

Try to automate user tasks
""".strip()


    try:
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
        )
        # This data will be passed to the "Router" and "Executor" nodes
        return {
            "messages": [response],
            "previous_actions": previous_actions[-10:],
            "retry_count": 0,
        }
    except Exception as err:
        return {
            "messages": [AIMessage(f"Strategist Error: {str(err)}")],
            "status": "failed",
        }
