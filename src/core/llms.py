import os
from dotenv import load_dotenv

from core.callbacks import SummaryCaptureHandler

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def _get_agent_llm():
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
    )


def _get_summarization_llm():
    """
    Returns an llm for the summarization
    """
    load_dotenv()

    # You can switch models here easily
    model_name = os.getenv("SUMMARIZATION_LLM", "google/gemma-3-12b-it")

    if "claude" in model_name:
        return ChatAnthropic(model=model_name, temperature=0)

    return ChatOpenAI(
        model=model_name,
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        streaming=True,
        callbacks=[SummaryCaptureHandler()],
    )


def _get_vision_model():
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


agent_llm = _get_agent_llm()
summarization_llm = _get_summarization_llm()
vision_model = _get_vision_model()
