import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from bs4 import BeautifulSoup

# Assuming this import remains the same
from perception.vision import VisionAnalyzer


class BrowserManager:
    def __init__(self):
        from core.llms import get_vision_model

        self.driver = Driver(
            browser="chrome",
            uc=True,
            headless=False,
            binary_location=r"C:\Program Files (x86)\chrome\chrome.exe",
            locale_code="en",
            
        )

        self.vision = VisionAnalyzer(get_vision_model())
        self.wait = WebDriverWait(self.driver, 1)

    def navigate_to(self, url: str) -> None:
        """Navigates to a specified URL."""
        try:
            self.driver.get(url)
            # Optional: Short sleep to let animations settle
            time.sleep(2)
        except Exception as e:
            print(f"Navigation error: {e}")

    def get_visual_context(self, query: str = None) -> str:
        """Analyzes the current screen visually."""
        prompt = query or (
            "Describe the current page layout, focusing on interactive elements "
            "(buttons, inputs, menus). If there are errors or popups, describe them."
        )

        print(f"Vision: Analyzing screen for '{prompt}'...")
        return self.vision.analyze_page(self.driver, prompt)

    def click_element(self, selector: str, by_method: str = "id") -> str:
        """
        THE HANDS: Smart clicking with Fallback.
        1. Waits for element to be clickable.
        2. Tries standard click.
        3. If blocked, forces click via JavaScript.
        """
        try:
            element = self._select_element(selector, by_method)

            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                element.click()
                return "Clicked (Standard)"

            except (ElementClickInterceptedException, ElementNotInteractableException):
                print(
                    f"Standard click failed for {selector}. Attempting JS Force Click..."
                )
                self.driver.execute_script("arguments[0].click();", element)
                return "Clicked (Forced via JS)"

        except TimeoutException:
            return (
                f"Error: Element {selector} not found or not clickable within timeout."
            )
        except Exception as err:
            return f"Error clicking element {selector}: {str(err)}"

    def insert_text(self, text: str, selector: str, by_method: str = "id") -> str:
        """Inserts text safely by ensuring the field is clear and active."""
        try:
            element = self._select_element(selector, by_method)

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )

            try:
                element.click()
            except:
                pass  # If click fails, we still try to type

            # Clear and Type
            element.clear()
            element.send_keys(text)
            element.send_keys(Keys.RETURN)
            return "Text inserted"
        except Exception as err:
            return f"Error inserting text into element {selector}: {str(err)}"

    def get_compressed_dom(self):
        """
        Extracts only interactive elements and text to save tokens.
        """
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        for script in soup(["script", "style", "svg", "path", "noscript"]):
            script.decompose()

        relevant_elements = []
        # Added 'textarea' and 'select' to your list for better form coverage
        for tag in soup.find_all(
            ["a", "button", "input", "textarea", "select", "h1", "h2", "p"]
        ):
            text = tag.get_text(strip=True)
            # Only include elements that have text OR are inputs
            if text or tag.name in ["input", "textarea", "select", "button"]:
                info = (
                    f"Tag: <{tag.name}> | "
                    f"Text: {text[:50]} | "
                    f"ID: {tag.get('id', 'N/A')} | "
                    f"Class: {' '.join(tag.get('class', []))}"
                )
                relevant_elements.append(info)

        return "\n".join(relevant_elements[:150])

    def _select_element(self, selector: str, by_method: str = "id"):
        """
        Internal method: Finds element with Explicit Wait.
        This prevents 'ElementNotFound' errors when the page is slow.
        """
        strategy = getattr(By, by_method.upper(), By.CSS_SELECTOR)

        # Wait up to 10 seconds for the element to exist and be visible
        element = self.wait.until(EC.presence_of_element_located((strategy, selector)))
        return element


# Usage
browser = BrowserManager()
driver = browser.driver
