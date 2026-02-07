from typing import List, Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.base import BaseMessage

from core.state import AgentState
from core.prompts import SYSTEM_PROMPT
from core.llms import get_agent_llm, get_summarization_llm

from config.logger import get_logger

from execution.tools import get_agent_tools


llm = get_agent_llm(get_agent_tools(get_summarization_llm()))
logger = get_logger("planning.strategist")


def strategist_node(state: AgentState) -> Dict[Any, Any]:
    """
    The Main Logic Node.
    Args:
        state: The current AgentState (dict)
    """
    messages: List[BaseMessage] = state.get("messages", [])
    previous_actions = state.get("previous_actions", [])

    # We grab the last few logs to give the agent "short-term memory"
    # recent_history = "\n - ".join(previous_actions[-10:])
    recent_history = "\n".join(msg.content for msg in messages[-10:])

    user_message = f"""
## USER GOAL:
{state['user_goal']}

## Previous Actions:
{recent_history}

Try to automate user tasks
""".strip()

    try:
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
            if not state["messages"]
            else state["messages"] + [HumanMessage(content="What you need to do next?")]
        )
        logger.info(response.content.strip())
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
