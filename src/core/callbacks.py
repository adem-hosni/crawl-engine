from config.logger import get_logger
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


logger = get_logger("core.callbacks")


class SummaryCaptureHandler(BaseCallbackHandler):
    """
    Captures the output of the summarization model in real-time.
    """

    def on_llm_start(
        self,
        serialized,
        prompts: list[str],
        *,
        run_id,
        parent_run_id=None,
        tags=None,
        metadata=None,
        **kwargs,
    ):
        logger.info(f"Summarization triggered on {len(prompts[0])} chars...")

    def on_llm_end(self, response: LLMResult, *, run_id, parent_run_id=None, **kwargs):
        try:
            summary_text = response.generations[0][0].text

            logger.info(f"[SUMMARY]: {summary_text:.130}...")
        except Exception as e:
            logger.error(f"Failed to capture summary")
