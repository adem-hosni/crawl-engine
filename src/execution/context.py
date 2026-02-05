"""Holds execution context singletons."""


class BrowserContext:
    """
    A simple singleton to hold the mapping between IDs and Selenium Selectors.
    This allows tools to resolve '[12]' to '//div[@id="submit"]' without
    needing to pass the huge map as an argument.
    """

    _element_map = {}

    @classmethod
    def set_map(cls, new_map: dict):
        cls._element_map = new_map

    @classmethod
    def get_selector(cls, element_id: int):
        # Ensure we handle both string "12" and int 12
        return cls._element_map.get(int(element_id))
