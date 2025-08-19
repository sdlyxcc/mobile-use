from typing import Optional


def find_element_by_resource_id(ui_hierarchy: list[dict], resource_id: str) -> Optional[dict]:
    """
    Find a UI element by its resource-id in the UI hierarchy.

    Args:
        ui_hierarchy: List of UI element dictionaries
        resource_id: The resource-id to search for
            (e.g., "com.google.android.settings.intelligence:id/open_search_view_edit_text")

    Returns:
        The complete UI element dictionary if found, None otherwise
    """

    def search_recursive(elements: list[dict]) -> Optional[dict]:
        for element in elements:
            if isinstance(element, dict):
                if element.get("resourceId") == resource_id:
                    return element

                children = element.get("children", [])
                if children:
                    result = search_recursive(children)
                    if result:
                        return result
        return None

    return search_recursive(ui_hierarchy)
