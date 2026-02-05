from langgraph.graph import StateGraph, END
from core.state import AgentState

from graph.nodes import perception_node, executor_node, router_node
from planning.strategist import strategist_node


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("perception", perception_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("executor", executor_node)

    workflow.set_entry_point("perception")

    workflow.add_edge("perception", "strategist")

    workflow.add_conditional_edges(
        "strategist", router_node, {"executor": "executor", "end": END}
    )

    workflow.add_edge("executor", "perception")  # Loop back

    return workflow.compile()
