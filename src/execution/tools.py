"""This module defines tools for interacting with the browser."""

import os
import json
import time
from langchain_core.tools import tool

from execution.browser import browser, driver
from execution.context import BrowserContext
from perception.dom_cleaner import DOMCleaner

from bs4 import BeautifulSoup, Comment

from selenium.common.exceptions import WebDriverException


# --- HELPERS ---
def _resolve_selector(element_id: int) -> str:
    """
    Helper to resolve ID -> XPath Selector.
    We no longer return the WebElement directly, but the selector string,
    so the BrowserManager can handle the 'finding' safely with waits.
    """
    xpath = BrowserContext.get_selector(element_id)
    if not xpath:
        raise ValueError(
            f"Element ID [{element_id}] is invalid or not in the current view."
        )
    return xpath


# --- TOOLS ---


@tool
def analyze_screen(query: str):
    """
    Captures a screenshot and uses Vision AI to analyze the page.
    Use this when:
    1. You are stuck or see "Element not interactable" errors.
    2. You cannot find an element in the HTML.
    3. You need to visually validate a chart, color, or layout.

    Args:
        query (str): A specific question (e.g., "Is there a popup blocking the center?").
    """
    return browser.get_visual_context(query)


@tool(
    description="Clicks on an interactive element identified by its numeric ID [x]. Example: click_element(element_id=5)"
)
def click_element(element_id: int):
    """
    Clicks on an interactive element identified by its numeric ID [x].
    Uses 'Smart Clicking' to handle popups and overlays automatically.
    """
    try:
        xpath = _resolve_selector(element_id)

        result = browser.click_element(selector=xpath, by_method="xpath")

        return f"Action on [{element_id}]: {result}"

    except Exception as e:
        return f"Error clicking element [{element_id}]: {str(e):.90}"


@tool(
    description="Types text into an input field identified by its numeric ID [x]. Example: insert_text(element_id=12, text='hello@example.com')"
)
def insert_text(element_id: int, text: str):
    """
    Types text into an input field identified by its numeric ID [x].
    Automatically focuses and clears the field before typing.
    """
    try:
        xpath = _resolve_selector(element_id)
        result = browser.insert_text(text=text, selector=xpath, by_method="xpath")
        return f"Action on [{element_id}]: {result}"

    except Exception as e:
        return f"Error typing into element [{element_id}]: {str(e):.90}"


@tool(
    description="Navigates the browser to a specific URL. Example: navigate_url(url='https://google.com')"
)
def navigate_url(url: str):
    """
    Navigates the browser to a specific URL.
    """
    try:
        browser.navigate_to(url)
        return f"Navigated to {url}"
    except Exception as e:
        return f"Error navigating to {url}: {str(e):.90}"


@tool
def scroll_element(element_id: int):
    """
    Scrolls the page until the element [x] is visible.
    """
    try:
        xpath = _resolve_selector(element_id)

        # We can use the internal driver here for simple scrolling,
        # but let's use the safer _select_element from BrowserManager if possible
        # to ensure the element actually exists before we try to scroll to it.
        element = browser._select_element(xpath, by_method="xpath")

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
            element,
        )
        time.sleep(0.5)  # Allow smooth scroll to finish
        return f"Scrolled to element [{element_id}]"

    except Exception as e:
        return f"Error scrolling to [{element_id}]: {str(e):.90}"


# @tool(description="Read page Interactive elements")
def read_interactive_elements() -> str:
    """
    Extracts interactive elements from the DOM.
    """
    try:
        return browser.get_compressed_dom()
    except Exception as err:
        return f"Error while reading page interactive elements: {str(err):.90}"


@tool(
    description="Use this ONLY when you are stuck, confused, or need a login code/password. "
    "It pauses execution, asks the human user a question, and saves the answer. "
    "Input: A clear question for the user."
)
def ask_user_for_help(question: str) -> str:
    """
    Pauses the agent to ask the human user a question via the console.
    Saves the answer to 'agent_knowledge.json' for future reference.
    """
    print(f"\n\n🤖 AGENT NEEDS HELP: {question}")
    print("---------------------------------------------------------")

    # 1. Get input from the human (Pauses execution here)
    user_answer = input("👤 YOUR ANSWER (Type here): ").strip()

    if not user_answer:
        return "User provided no input. Try looking for the answer on the page again."

    # 2. Save the new knowledge
    _save_knowledge(question, user_answer)

    return f"The user answered: '{user_answer}'. Use this information to proceed."


KNOWLEDGE_FILE = "agent_knowledge.json"


def _save_knowledge(question: str, answer: str):
    """Helper to append Q&A to a local JSON file."""
    data = []
    if os.path.exists(KNOWLEDGE_FILE):
        try:
            with open(KNOWLEDGE_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass  # File might be empty or corrupted

    data.append(
        {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "answer": answer,
        }
    )

    with open(KNOWLEDGE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Knowledge saved to {KNOWLEDGE_FILE}")


@tool(
    description="Checks if the user has already answered a similar question in the past."
)
def check_saved_knowledge(query: str) -> str:
    if not os.path.exists(KNOWLEDGE_FILE):
        return "No saved knowledge found."

    try:
        with open(KNOWLEDGE_FILE, "r") as f:
            data = json.load(f)

        # Simple keyword match (You could upgrade this to vector search later)
        relevant_answers = [
            f"Q: {item['question']} | A: {item['answer']}"
            for item in data
            if any(word in item["question"].lower() for word in query.lower().split())
        ]

        if relevant_answers:
            return "Found past answers:\n" + "\n".join(relevant_answers)
        return "No relevant past answers found."

    except Exception:
        return "Error reading knowledge file."


@tool(
    description="Executes raw JavaScript code with no comments in the browser. "
    "Use this as a LAST RESORT when standard click/type tools fail due to "
    "'Element not interactable' or 'interception' errors. "
    "You can use this to force-click elements, remove blocking overlays, or scroll. "
    "Example: execute_javascript(code=\"document.getElementById('submit-btn').click()\")"
)
def execute_javascript(code: str) -> str:
    """
    Executes raw JavaScript code in the current browser context.
    Returns the result of the execution (if any).
    """
    try:
        result = driver.execute_script(code)
        if result is not None:
            return f"Result: {str(result)}"
        return "JavaScript executed successfully (no return value)."
    except Exception as e:
        return f"System Error executing JS: {str(e):.90}"


@tool(parse_docstring=True)
def read_page_content():
    """
    Scans the current page and returns a simplified, clean HTML representation.
    CRITICAL: This tool assigns numeric IDs (e.g., [12]) to interactive elements.
    You MUST use these IDs with the click_element and insert_text tools.
    """
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Remove html comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        for tag in soup(
            [
                "script",
                "style",
                "svg",
                "path",
                "footer",
                "meta",
                "link",
                "noscript",
                "use",
                "hr",
            ]
        ):
            tag.decompose()
        attrs_to_remove = {
            "style",
            "class",
            "width",
            "height",
            "data-",
            "aria-",
            "autoplay",
            "crossorigin",
            "rel",
            "accept",
            "tab-",
            "target",
            "method",
            "referrerpolicy",
            "novalidate",
            "dir",
            "role",
            "xmlns",
            "fill",
            "d",
        }

        def remove_attrs(body):
            for element in body.find_all(True):
                for attr in [
                    attr
                    for attr in element.attrs
                    if any(prefix in attr for prefix in attrs_to_remove)
                ]:
                    del element.attrs[attr]
            return body

        source = str(remove_attrs(soup.body)).replace("\n", "")

        chunks = {
            "  ": " ",
            "</div></div>": "</div>",
            "<div><div>": "<div>",
            "<div></div>": "",
            "<span><span>": "<span>",
            "</span></span>": "</span>",
            "<span></span>": "<span>",
        }

        while any([source.count(chunk) > 0 for chunk in chunks.keys()]):
            for k, v in chunks.items():
                source = source.replace(k, v)
            
        # cleaner = DOMCleaner()

        print(f"Source size: {len(source)} bytes")
        return source

        # return cleaner.clean_and_map(driver.page_source)
    except Exception as err:
        return f"Error while reading page source code: {str(err)[:200]}"


@tool
def refresh_page(wait_time: int = 3):
    """
    Refreshes the current web page.
    Use this when the page seems stuck, elements are not loading,
    or you need to reset the view to the initial state.

    Args:
        wait_time: Time in seconds to wait after refreshing (default is 3).
    """
    try:
        print(f"🔄 Refreshing page...")
        driver.refresh()

        time.sleep(wait_time)

        return f"Successfully refreshed the page and waited {wait_time} seconds."

    except WebDriverException as e:
        return f"Error: Failed to refresh the page. Details: {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred during refresh: {str(e)}"


TOOLS = [
    click_element,
    insert_text,
    navigate_url,
    execute_javascript,
    read_page_content,
    ask_user_for_help,
    check_saved_knowledge,
    refresh_page,
    # analyze_screen,
]
