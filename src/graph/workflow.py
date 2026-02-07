from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from core.llms import get_summarization_llm
from core.state import AgentState
from graph.nodes import (
    perception_node,
    summarization_node,
    should_summarize_route,
    router_node,
)

from execution.tools import get_agent_tools
from planning.strategist import strategist_node


def build_graph():
    toolnode = ToolNode(get_agent_tools(get_summarization_llm()))

    workflow = StateGraph(AgentState)

    workflow.add_node("perception", perception_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("executor", toolnode)
    # workflow.add_node("summarizer", summarization_node)

    workflow.set_entry_point("perception")

    workflow.add_edge("perception", "strategist")

    workflow.add_conditional_edges(
        "strategist", router_node, {"executor": "executor", "end": END}
    )

    # workflow.add_conditional_edges(
    #     "executor", should_summarize_route, {"summarizer": "summarizer", "perception": "perception"}
    # )

    workflow.add_edge("executor", "perception")  # Loop back

    return workflow.compile()
