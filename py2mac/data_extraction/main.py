#    Copyright (c) 2024 Rafal Wytrykus
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
This module provides functions to clean and flatten UI data structures.
"""

import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def _flatten_elements(element: Dict[str, Any]) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    """
    Flatten the given element if it is redundant, otherwise process its children.

    Args:
        element (Dict[str, Any]): The UI element to process.

    Returns:
        Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
            - A single element if it should be kept as is.
            - A list of elements if it has been flattened.
            - None if the element should be removed.
    """
    if _should_remove_element(element):
        # If the element should be removed, return None
        return None
    if "children" in element:
        if _can_flatten(element):
            logger.debug(f"Flattening {element['id']} element")
            # If the element can be flattened, return the flattened children
            return _flatten_children(element["children"])
        elif _can_merge_text_children(element):
            # If the element can merge its text children, perform the merge
            element = _merge_text_children(element)
        else:
            # Otherwise, recursively flatten all children
            element["children"] = _flatten_children(element["children"])
            if not element["children"]:
                # Remove the 'children' key if there are no children left
                element.pop("children")

    if not element.get("actions"):
        # Remove the 'id' if there are no actions associated with the element
        element.pop("id", None)

    return element


def _should_remove_element(element: Dict[str, Any]) -> bool:
    """
    Determine if an element should be removed from the tree based on its properties.

    Args:
        element (Dict[str, Any]): The UI element to evaluate.

    Returns:
        bool: True if the element should be removed, False otherwise.
    """
    # Remove empty groups and non-informative images
    return (
        not element.get("children")
        and not element.get("AXValue")
        and not element.get("AXTitle")
        and not element.get("actions")
    )


def _can_flatten(element: Dict[str, Any]) -> bool:
    """
    Determine if the element can be flattened.

    Args:
        element (Dict[str, Any]): The UI element to evaluate.

    Returns:
        bool: True if the element can be flattened, False otherwise.
    """
    # Criteria for flattening: an element with no significant actions or descriptions,
    # and of certain roles
    can_flatten = (
        element["AXRole"] in ["AXGroup", "AXSplitGroup", "AXTabGroup", "AXScrollArea", "AXSplitter"]
        and not element.get("actions")
        and not element.get("AXDescription")
        and not element.get("AXRoleDescription")
        and not element.get("AXValue")
        and not element.get("AXTitle")
    )
    return can_flatten


def _can_merge_text_children(element: Dict[str, Any]) -> bool:
    """
    Check if all children of this element are text and can be merged.

    Args:
        element (Dict[str, Any]): The UI element to evaluate.

    Returns:
        bool: True if all children are text and can be merged, False otherwise.
    """
    return all(child.get("AXRole") == "AXStaticText" for child in element.get("children", []))


def _merge_text_children(element: Dict[str, Any]) -> Dict[str, Any]:
    """
    Concatenate all child text elements into a single 'AXValue' in the parent.

    Args:
        element (Dict[str, Any]): The UI element whose text children will be merged.

    Returns:
        Dict[str, Any]: The modified UI element with merged text children.
    """
    combined_text = "".join(child.get("AXValue", "") for child in element.get("children", []))
    # Create a single child element with the combined text
    element["children"] = [
        {
            # "id": "combined_text__" + element.get('id', ''),
            "AXRoleDescription": "combined text",
            "AXRole": "AXStaticText",
            "AXValue": combined_text,
        }
    ]
    return element


def _flatten_children(children: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recursively process a list of children, flattening where applicable.

    Args:
        children (List[Dict[str, Any]]): The list of child elements to process.

    Returns:
        List[Dict[str, Any]]: The list of processed child elements.
    """
    flattened = []
    for child in children:
        result = _flatten_elements(child)
        if not result:
            # Skip None results
            continue
        # If the child was flattened to a list, extend the list; otherwise, append the result
        if isinstance(result, list):
            flattened.extend(result)
        else:
            flattened.append(result)
    return flattened


def clean_ui_tree(ui_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean the UI data by flattening redundant components and simplifying the structure.

    Args:
        ui_data (Dict[str, Any]): The UI data to clean.

    Returns:
        Dict[str, Any]: The cleaned UI data.
    """
    if "children" in ui_data:
        ui_data["children"] = _flatten_children(ui_data["children"])
    return ui_data


def flatten_ui_tree(component_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flatten the UI tree into a list of components.

    Args:
        component_tree (Dict[str, Any]): The component tree to flatten.

    Returns:
        List[Dict[str, Any]]: A list of components with hierarchical structure removed.
    """
    flat_component_tree: List[Dict[str, Any]] = []

    def _flatten_component_tree(
        node: Dict[str, Any],
        accumulator: List[Dict[str, Any]],
    ) -> None:
        accumulator.append({k: v for k, v in node.items() if k != "children"})
        for child in node.get("children", []):
            _flatten_component_tree(child, accumulator)

    _flatten_component_tree(component_tree, flat_component_tree)

    return flat_component_tree
