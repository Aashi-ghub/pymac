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
This module provides classes and functions for interacting with UI elements via the macOS Accessibility API.
"""

from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any, Collection, Optional

import ApplicationServices as AS
from attr import define

from py2mac.exceptions import UIActionError, UIAttributeAccessError

if TYPE_CHECKING:
    from py2mac.application import Application

logger = logging.getLogger(__name__)


class UIElement:
    """
    Represents a UI element in a macOS application, providing methods to interact with it via the Accessibility API.
    """

    _handle: AS.AXUIElementRef
    _application: Application
    _parent_ui_element: Optional[UIElement]

    def __init__(self, handle, application, parent_ui_element=None):
        """
        Initialize a UIElement instance.

        Args:
            handle (AS.AXUIElementRef): The accessibility element handle.
            application (Application): The Application instance this UIElement is part of.
            parent_ui_element (Optional[UIElement]): The parent UIElement, if any.

        Side Effects:
            Populates the `_ui_elements` dictionary of the application with this UIElement.
            Dynamically adds action methods to this instance based on available actions.
        """
        self._handle = handle
        self._application = application
        self._parent_ui_element = parent_ui_element
        for action_name in self.actions:
            setattr(self, action_name, UIAction(action_name, self._handle, self))

        self.id = self._get_id()
        self._application._ui_elements[self.id] = self

    def _get_id(self) -> str:
        """
        Generate a unique identifier for the UIElement.

        Returns:
            str: A unique ID for the UIElement.
        """
        return self._get_id_pretty()

    def _get_id_simple(self) -> str:
        """
        Generate a simple unique identifier based on the AXRole and object's hash.

        Returns:
            str: A simple unique ID.
        """
        return f"{getattr(self, 'AXRole', '')}{hash(self)}"

    def _get_id_pretty(self) -> str:
        """
        Generate a more descriptive unique identifier including role and title.

        Returns:
            str: A descriptive unique ID.
        """
        role_description = getattr(self, "AXRoleDescription", None)
        if role_description:
            role_text = role_description.replace(" ", "_")
        else:
            role_text = getattr(self, "AXRole", "")

        extras = []
        title = getattr(self, "AXTitle", None) or getattr(self, "AXDescription", None) or getattr(self, "AXValue", None)
        if title is not None:
            title = title[:32] if isinstance(title, str) else str(title)
            title_text = "".join(e for e in str(title).lower().replace(" ", "_") if e.isalnum() or e == "_")
            extras.append(title_text)

        extras_text = f"__{'_'.join(extras)}" if extras else ""

        return f"{role_text}{extras_text}__{hash(self)}"

    @cached_property
    def attributes(self) -> list[str]:
        """
        Retrieve the list of attribute names available for this UIElement.

        Returns:
            list[str]: A list of attribute names.

        Note:
            Uses `cached_property` to avoid redundant API calls.
        """
        error, attributes = AS.AXUIElementCopyAttributeNames(self._handle, None)
        if error != AS.kAXErrorSuccess:
            return []
            # raise ValueError(f"Error {error} while trying to get attributes")
        return attributes

    @cached_property
    def settable_attributes(self) -> list[str]:
        """
        Retrieve the list of attribute names available for this UIElement.

        Returns:
            list[str]: A list of attribute names.

        Note:
            Uses `cached_property` to avoid redundant API calls.

        :return:
        """
        return [attr for attr in self.attributes if self.is_attribute_settable(attr)]

    def is_attribute_settable(self, attribute: str) -> bool:
        """
        Check if an attribute is settable for this UIElement.

        Args:
            attribute (str): The attribute name.

        Returns:
            bool: True if the attribute is settable, False otherwise.
        """
        error, settable = AS.AXUIElementIsAttributeSettable(self._handle, attribute, None)
        if error != AS.kAXErrorSuccess:
            raise UIAttributeAccessError(f"Error {error} while trying to check if attribute {attribute} is settable")
        return settable

    def __len__(self) -> int:
        """
        Get the number of attributes available for this UIElement.

        Returns:
            int: The number of attributes.
        """
        return len(self.attributes)

    def __repr__(self) -> str:
        """
        Return the string representation of the UIElement.

        Returns:
            str: The string representation.
        """
        return f"<UIElement '{self}'>"

    def __str__(self) -> str:
        """
        Return the user-friendly string representation of the UIElement.

        Returns:
            str: The title of the UIElement or its handle representation.
        """
        return getattr(self, AS.kAXTitleAttribute, None) or repr(self._handle)

    def __getattr__(self, item: str) -> Any:
        """
        Dynamically retrieve attributes from the UIElement.

        Args:
            item (str): The attribute name.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute is not found.
        """
        if item == "_handle":
            # Skip the _handle attribute to avoid infinite recursion
            return super().__getattr__(item)
        elif item in self.attributes:
            try:
                return self._get_attribute(item)
            except KeyError:
                return None
        raise AttributeError(f"Attribute {item} not found")

    def __setattr__(self, key: str, value: Any):
        """
        Set an attribute value on the UIElement.

        Args:
            key (str): The attribute name.
            value (Any): The value to set.

        Side Effects:
            Updates the attribute via the Accessibility API if it's an attribute of the UIElement.

        Note:
            If the attribute is not part of `_attribute_names`, it is set as a normal attribute.
        """
        if hasattr(self, key) and key in self.settable_attributes:
            logger.debug("Setting attribute %s of UIElement %s to %s", key, self, value)
            AS.AXUIElementSetAttributeValue(self._handle, key, value)
        super(UIElement, self).__setattr__(key, value)

    def __hasattr__(self, item: str) -> bool:
        """
        Check if the UIElement has a specific attribute.

        Args:
            item (str): The attribute name.

        Returns:
            bool: True if the attribute exists, False otherwise.
        """
        if item == "_handle":
            # Skip the _handle attribute to avoid infinite recursion
            return super().__hasattr__(item)
        return item in self.attributes

    def __dir__(self) -> list[str]:
        """
        List available attributes and methods for the UIElement.

        Returns:
            list[str]: A list of attribute and method names.
        """
        return super.__dir__(self) + self.attributes

    def _get_attribute(self, name: str) -> Any:
        """
        Retrieve the value of an attribute from the UIElement.

        Args:
            name (str): The attribute name.

        Returns:
            Any: The value of the attribute.

        Raises:
            KeyError: If an error occurs while retrieving the attribute.
        """
        err, value = AS.AXUIElementCopyAttributeValue(self._handle, name, None)
        if err != AS.kAXErrorSuccess:
            raise KeyError(f"Error {err} while trying to get attribute {name}")
        return value

    @cached_property
    def actions(self) -> list[str]:
        """
        Get a list of all actions that can be performed on this UIElement.

        Actions can be performed by calling the action as a method on the UIElement.

        Example:
            element = UIElement(handle)
            element.AXPress()

        Returns:
            list[str]: A list of action names.
        """
        error, actions = AS.AXUIElementCopyActionNames(self._handle, None)
        if error != AS.kAXErrorSuccess:
            return []
            # raise ValueError(f"Error {error} while trying to get actions")
        return [str(action) for action in actions]

    @property
    def _actions(self) -> dict[str, UIAction]:
        """
        Get a dictionary of UIAction instances for available actions.

        Returns:
            dict[str, UIAction]: A dictionary mapping action names to UIAction instances.
        """
        return {name: UIAction(name, self._handle, self) for name in self.actions}

    @property
    def children(self) -> list["UIElement"]:
        """
        Get the child UIElements of this UIElement.

        Returns:
            list[UIElement]: A list of child UIElements.

        Note:
            If the UIElement has no children, an empty list is returned.
        """
        try:
            children = self._get_attribute("AXChildren")
        except KeyError:
            return []
        return [UIElement(handle, self._application, self) for handle in children]

    @property
    def path(self) -> list["UIElement"]:
        """
        Get the path from the root UIElement to this UIElement.

        Returns:
            list[UIElement]: A list of UIElements representing the path.
        """
        path = []
        current: Optional["UIElement"] = self
        while current:
            path.append(current)
            current = current._parent_ui_element
        return path[::-1]

    @property
    def path_str(self) -> str:
        """
        Get a string representation of the UIElement's path.

        Returns:
            str: A string showing the path of UIElements separated by '->'.
        """
        return " -> ".join(str(element) for element in self.path)

    def items(self) -> list[tuple[str, Any]]:
        """
        Get a list of attribute-value pairs for the UIElement.

        Returns:
            list[tuple[str, Any]]: A list of (attribute name, value) tuples.
        """
        return [(name, self._get_attribute(name)) for name in self.attributes]

    def asdict(
        self,
        include_children: bool = True,
        include_action_names: bool = True,
        included_attributes: Collection[str] | None = None,
        included_actions: Collection[str] | None = None,
        attributes_skipped_if_false: Collection[str] | None = None,
        include_path: bool = False,
        include_parent_id: bool = False,
        include_empty_attributes: bool = False,
        included_empty_attributes: Collection[str] | None = None,
    ) -> dict[str, Any]:
        """
        Convert the UIElement to a dictionary.

        Args:
            include_children (bool): Whether to include the children of the UIElement.
            include_action_names (bool): Whether to include the names of the actions that can be performed.
            included_attributes (Optional[Collection[str]]): Specific attributes to include. If None, all are included.
            included_actions (Optional[Collection[str]]): Specific actions to include. If None, all are included.
            attributes_skipped_if_false (Optional[Collection[str]]): Attributes to skip if their value is False. Default is ['AXSelected'].
            include_path (bool): Whether to include the path of the UIElement.
            include_parent_id (bool): Whether to include the ID of the parent UIElement.
            include_empty_attributes (bool): Whether to include attributes with empty values.
            included_empty_attributes (Optional[Collection[str]]): Specific empty attributes to include. If None and `include_empty_attributes=False`, no empty attributes are included.

        Returns:
            dict[str, Any]: A dictionary representation of the UIElement.
        """
        included_attributes = set(included_attributes) if included_attributes else None
        attributes_skipped_if_false = (
            set(attributes_skipped_if_false) if attributes_skipped_if_false else set(["AXSelected"])
        )
        included_actions = set(included_actions) if included_actions else None
        included_empty_attributes = set(included_empty_attributes) if included_empty_attributes else set()

        attrs = {
            name: getattr(self, name)
            for name in self.attributes
            if hasattr(self, name)
            and name != "AXChildren"
            and (included_attributes is None or name in included_attributes)
        }
        if include_path:
            attrs["path"] = [element.id for element in self.path]
        if include_parent_id:
            attrs["parent_id"] = self._parent_ui_element.id if self._parent_ui_element else None
        if not include_empty_attributes:
            # Remove empty attributes
            attrs = {k: v for k, v in attrs.items() if k not in included_empty_attributes and v is not None and v != ""}
        # Remove attributes that are False if specified
        attrs = {k: v for k, v in attrs.items() if k not in attributes_skipped_if_false or v}
        actions = [action for action in self.actions if included_actions is None or action in included_actions]

        result = {
            "id": self.id,
            **attrs,
            **({"actions": actions} if include_action_names and actions else {}),
        }

        if include_children and self.children:
            result["children"] = [
                child.asdict(
                    include_children,
                    include_action_names,
                    included_attributes,
                    included_actions,
                    attributes_skipped_if_false,
                    include_path,
                    include_parent_id,
                    include_empty_attributes,
                    included_empty_attributes,
                )
                for child in self.children
            ]

        return result


@define
class UIAction:
    """
    Represents an action that can be performed on a UIElement.

    Attributes:
        name (str): The name of the action.
        parent_ui_element (UIElement): The UIElement this action belongs to.

    Methods:
        __call__(self, *args, **kwargs): Executes the action.
    """

    name: str
    _handle: AS.AXUIElementRef
    parent_ui_element: UIElement

    def __init__(self, name: str, handle: AS.AXUIElementRef, parent_ui_element: UIElement):
        """
        Initialize a UIAction instance.
        """
        self.name = name
        self._handle = handle
        self.parent_ui_element = parent_ui_element

    def __call__(self, *args, **kwargs):
        """
        Execute the action on the UIElement.

        Raises:
            UIActionError: If an error occurs while performing the action.
        """
        error = AS.AXUIElementPerformAction(self._handle, self.name)
        if error != AS.kAXErrorSuccess:
            raise UIActionError(f"Error {error} while trying to perform action {self.name}")

    def __repr__(self) -> str:
        """
        Return the string representation of the UIAction.

        Returns:
            str: The string representation.
        """
        return f"<UIAction '{self.name}' of '{self.parent_ui_element}'>"
