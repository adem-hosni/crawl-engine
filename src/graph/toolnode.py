from typing import List, Callable, Any

from langchain_openai import ChatOpenAI
from langchain.agents.middleware import TodoListMiddleware, AgentMiddleware

from deepagents.backends.state import StateBackend
from deepagents.middleware.memory import MemoryMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.summarization import SummarizationMiddleware
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.subagents import (
    CompiledSubAgent,
    SubAgent,
    SubAgentMiddleware,
)

from execution.tools import (
    click_element,
    insert_text,
    navigate_url,
    execute_javascript,
    read_page_sourcecode,
    ask_user_for_help,
    check_saved_knowledge,
    refresh_page,
    analyze_screen,
)


def get_agent_tools(
    llm: ChatOpenAI,
    summarization_llm: ChatOpenAI,
    subagents: list[SubAgent | CompiledSubAgent] = [],
) -> List[Callable[..., Any]]:
    backend = lambda runtime: StateBackend(runtime)
    AGENT_TOOLS = [
        # click_element,
        # insert_text,
        navigate_url,
        execute_javascript,
        read_page_sourcecode,
        ask_user_for_help,
        check_saved_knowledge,
        refresh_page,
        analyze_screen,
    ]

    return AGENT_TOOLS + [
        tool
        for middleware in [
            TodoListMiddleware(),
            FilesystemMiddleware(backend=backend),
            SubAgentMiddleware(
                default_model=llm,
                default_tools=AGENT_TOOLS,
                subagents=subagents,
            ),
            PatchToolCallsMiddleware(),
            SummarizationMiddleware(model=summarization_llm, backend=backend),
            # MemoryMiddleware(backend=backend),
        ]
        for tool in getattr(middleware, "tools", [])
    ]


agent_tools = lambda **kwargs: get_agent_tools(**kwargs)
