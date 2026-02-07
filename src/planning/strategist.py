from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.base import BaseMessage

from core.state import AgentState
from core.prompts import SYSTEM_PROMPT

from config.logger import get_logger

logger = get_logger("planning.strategist")


def get_strategist_node(bound_agent_tools: ChatOpenAI):
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
    In order to complete the objective that the user asks of you, you have access to a number of standard tools.
    """.strip()

        try:
            response = bound_agent_tools.invoke(
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
    return strategist_node
