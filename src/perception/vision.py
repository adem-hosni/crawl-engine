import traceback
from undetected_chromedriver import Chrome

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class VisionAnalyzer:
    def __init__(self, model: ChatOpenAI):
        self.model = model

    def analyze_page(self, driver: Chrome, prompt: str) -> str:
        """Captures the current browser state and queries the Vision Model.

        Args:
            driver: The selenium webdriver instance (from execution.browser)
            prompt: The question (e.g., "Is the 'Submit' button visible?")

        Returns:
            str: Page visual content description
        """
        screenshot_b64 = driver.get_screenshot_as_base64()

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
                },
            ]
        )

        try:
            response = self.model.invoke([message])
            return response.content
        except Exception as err:
            print(f"Vision Error: {str(err)}")
            traceback.print_exc()
            return f"Error: Unable to analyze the visual content."
