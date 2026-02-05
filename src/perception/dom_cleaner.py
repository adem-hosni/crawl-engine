from bs4 import BeautifulSoup, Tag
import re


class DOMCleaner:
    def __init__(self):
        self.element_map = {}
        self.counter = 0

    def clean_and_map(self, raw_html: str) -> str:
        """
        Input: Raw Selenium HTML
        Output: Clean text like:
            [1] Button: Login
            [2] Input :Username
        """
        soup = BeautifulSoup(raw_html, "html.parser")
        self.element_map = {}
        self.counter = 0

        for tag in soup(
            ["script", "style", "svg", "path", "footer", "meta", "link", "noscript"]
        ):
            tag.decompose()

        output_lines = []
        for tag in soup.find_all(
            [
                "a",
                "button",
                "input",
                "textarea",
                "select",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "p",
                "pre",
            ]
        ):
            if self._is_visible(tag) or True:
                element_id = self.counter
                self.counter += 1

                description = self._describe_element(tag)
                output_lines.append(f"[{element_id}] {description}")

                self.element_map[element_id] = self._get_xpath(tag)
        return "\n".join(output_lines)

    def _describe_element(self, tag: Tag) -> str:
        tag_name = tag.name
        text = tag.get_text(strip=True)
        aria = tag.get("aria-label") or tag.get("title") or ""
        placeholder = tag.get("placeholder", "")

        def pick(*args):
            return next((s for s in args if s), "Unknown")

        match tag_name:
            case "a":
                return f"Link: {pick(text, aria, tag.get('href'))[:50]}"
            case "img":
                alt = tag.get("alt", "")
                src = tag.get("src", "").split("/")[-1]
                return f"Image: {pick(alt, aria, src)[:50]}"
            case "input":
                input_type = tag.get("type", "text")
                if input_type in ["submit", "button", "reset"]:
                    return f"Button: {pick(tag.get('value'), aria, 'Submit')}"
                if input_type in ["checkbox", "radio"]:
                    state = "checked" if tag.has_attr("checked") else "unchecked"
                    return f"{input_type.capitalize()} ({state}): {pick(aria, tag.get('name'), 'Option')}"
                return (
                    f"Input ({input_type}): {pick(placeholder, aria, tag.get('name'))}"
                )
            case "button":
                return f"Button: {pick(text, aria, 'Submit')}"
            case "select":
                return f"Dropdown: {pick(aria, tag.get('name'), 'Options')}"
            case "textarea":
                return f"Text Area: {pick(placeholder, aria, text)}"
            case "label":
                return f"Label: {pick(text, aria)}"
            case "p":
                return f"Paragraph: {pick(text, aria, tag.get("data-placeholder"))}"
            case h if h.startswith("h") and len(h) == 2:
                return f"Heading ({h}): {pick(text, aria)}"
            case "form":
                return f"Form: {pick(aria, tag.get('name'), tag.get('action'), 'Untitled')}"
            case _:
                return f"{tag_name}: {pick(text, aria)[:50]}"

    def _is_visible(self, tag: Tag) -> bool:
        """Check if a tag is visible and interactive."""
        if tag.has_attr("hidden") or tag.get("type") == "hidden":
            return False
        return True

    def _get_xpath(self, element: Tag) -> str:
        """Generate a simple XPath for the element."""
        if element.get("id"):
            return f"//{element.name}[@id='{element['id']}']"
        if element.get("name"):
            return f"//{element.name}[@name='{element['name']}']"
        if element.get("class"):
            return f"//{element.name}[@class='{' '.join(element['class'])}']"

        text = element.get_text(strip=True)
        if text:
            quote = '"' if "'" in text else "'"
            return f"//{element.name}[text()={quote}{text}{quote}]"

        # Fallback
        return f"//{element.name}"
