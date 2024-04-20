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
This module provides factory functions to create LangChain tools for interacting with UI elements via the
macOS Accessibility API using Py2Mac package.
"""

import json
from typing import Callable, List, Optional

from langchain_core.tools import tool

import py2mac.data_extraction
from py2mac.application import Application
from py2mac.json_utils import json_serializable


def get_ui_state_tool(
    application: Application,
    included_attributes: Optional[List[str]] = None,
    included_actions: Optional[List[str]] = None,
    clean_up_ui_tree: bool = True,
    flatten_ui_tree: bool = True,
) -> Callable[[], str]:
    """
    Create a LangChain tool to get the current state of the UI elements of an application.

    Args:
        application (Application): The application instance to interact with.
        included_attributes (Optional[List[str]]): A list of attribute names to include in the UI state.
            Defaults to a predefined list of common attributes if None.
        included_actions (Optional[List[str]]): A list of action names to include.
            Defaults to ["AXPress"] if None.
        clean_up_ui_tree (bool): Whether to clean up the UI tree by removing redundant elements.
            Defaults to True.
        flatten_ui_tree (bool): Whether to flatten the UI tree into a list of components.
            Defaults to True.

    Returns:
        Callable[[], str]: An asynchronous function langchain tool that retrieves the UI state as a JSON string.
    """
    _included_attributes = included_attributes or [
        "AXTitle",
        "AXRole",
        "AXValue",
        "AXDescription",
        "AXPlaceholderValue",
        "AXSelected",
        "AXSubrole",
        "AXRoleDescription",
    ]

    _included_actions = included_actions or ["AXPress"]

    @tool
    async def get_ui_state() -> str:
        """
        Get the current state of the UI elements of the application.

        Returns:
            str: A JSON-formatted string representing the UI state.
        """
        application.refresh_ui_tree()
        ui_tree = application.root_ui_element.asdict(
            included_attributes=_included_attributes,
            included_actions=_included_actions,
        )
        if clean_up_ui_tree:
            ui_tree = py2mac.data_extraction.clean_ui_tree(ui_tree)
        if flatten_ui_tree:
            ui_tree = py2mac.data_extraction.flatten_ui_tree(ui_tree)

        return json.dumps(json_serializable(ui_tree))

    return get_ui_state


def get_ui_set_attribute_tool(
    application: Application,
    require_confirmation: bool = True,
) -> Callable[[str, str, str], str]:
    """
    Create a LangChain tool to set an attribute of a UI element.

    Args:
        application (Application): The application instance to interact with.
        require_confirmation (bool): Whether to require user confirmation before setting the attribute.
            Defaults to True.

    Returns:
        Callable[[str, str, str], str]: An asynchronous function langchain tool that sets a UI element's attribute.
    """

    @tool
    async def set_ui_attribute(component_id: str, attribute_name: str, attribute_value: str) -> str:
        """
        Set an attribute of a UI element.

        Args:
            component_id (str): The ID of the UI element.
            attribute_name (str): The name of the attribute to set.
            attribute_value (str): The value to set for the attribute.

        Returns:
            str: A message indicating the result of the operation.
        """
        ui_element = application.get_ui_element(component_id)
        if require_confirmation:
            should_continue = input(
                f"Set attribute '{attribute_name}' to '{attribute_value}' for UI element '{component_id}'? (y/n) "
            )
            if should_continue.lower() != "y":
                return "Operation cancelled."
        setattr(ui_element, attribute_name, attribute_value)
        return f"Set attribute '{attribute_name}' to '{attribute_value}' for UI element '{component_id}'."

    return set_ui_attribute


def get_ui_action_tool(
    application: Application,
    require_confirmation: bool = True,
) -> Callable[[str, str], str]:
    """
    Create a LangChain tool to trigger an action on a UI element.

    Args:
        application (Application): The application instance to interact with.
        require_confirmation (bool): Whether to require user confirmation before triggering the action.
            Defaults to True.

    Returns:
        Callable[[str, str], str]: An asynchronous function langchain tool that triggers an action on a UI element.
    """

    @tool
    async def trigger_ui_action(component_id: str, action_name: str) -> str:
        """
        Trigger an action on a UI element.

        Args:
            component_id (str): The ID of the UI element.
            action_name (str): The name of the action to trigger.

        Returns:
            str: A message indicating the result of the operation.
        """
        ui_element = application.get_ui_element(component_id)
        if require_confirmation:
            should_continue = input(f"Trigger action '{action_name}' for UI element '{component_id}'? (y/n) ")
            if should_continue.lower() != "y":
                return "Operation cancelled."
        getattr(ui_element, action_name)()
        return f"Triggered action '{action_name}' for UI element '{component_id}'."

    return trigger_ui_action
