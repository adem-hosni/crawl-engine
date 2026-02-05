import os
from dotenv import load_dotenv
from typing import List, Callable, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic  # Optional: if you want Claude later


def get_agent_llm(tools: List[Callable[..., Any]]):
    """
    Returns the configured LLM for the Agent.
    """
    load_dotenv()

    # You can switch models here easily
    model_name = os.getenv("LLM_MODEL", "deepseek/deepseek-v3.2")

    if "claude" in model_name:
        return ChatAnthropic(model=model_name, temperature=0)

    return ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        streaming=True,
    ).bind_tools(tools)


def get_vision_model():
    """
    Returns the configured LLM for the Agent.
    """
    load_dotenv()

    # You can switch models here easily
    model_name = os.getenv("VISION_MODEL", "qwen/qwen2.5-vl-32b-instruct")

    return ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=1000,
        streaming=True,
    )
