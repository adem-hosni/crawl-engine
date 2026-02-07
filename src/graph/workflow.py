from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver

from core.llms import agent_llm as llm, summarization_llm
from core.state import AgentState
from graph.nodes import (
    perception_node,
    summarization_node,
    should_summarize_route,
    router_node,
)
from graph.toolnode import agent_tools

from planning.strategist import get_strategist_node


def build_graph():
    tools = agent_tools(llm=llm, summarization_llm=summarization_llm)
    agent_llm = llm.bind_tools(tools)

    workflow = StateGraph(AgentState)

    workflow.add_node("perception", perception_node)
    workflow.add_node("strategist", get_strategist_node(agent_llm))
    workflow.add_node("executor", ToolNode(tools))
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

    return workflow.compile(checkpointer=InMemorySaver())
