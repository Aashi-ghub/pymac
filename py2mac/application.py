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
This module provides the `Application` class for interacting with running macOS applications via the Accessibility API.
"""
from __future__ import annotations

import ApplicationServices as AS
from AppKit import NSWorkspace

from py2mac.ui import UIElement


class Application:
    """
    A class representing a running macOS application, providing methods to interact with its UI elements via the Accessibility API.

    Attributes:
        pid (int): The process identifier of the application.
        application (AS.AXUIElementRef): The accessibility element representing the application.
        running_application (AS.NSRunningApplication): The NSRunningApplication instance representing the application.
    """

    def __init__(self, application: AS.NSRunningApplication):
        """
        Initialize an Application instance.

        Args:
            application (AS.NSRunningApplication): The NSRunningApplication instance representing the application.
        """
        self.pid = application.processIdentifier()
        self.application = AS.AXUIElementCreateApplication(self.pid)
        self.running_application = application

        self._ui_elements: dict[str, UIElement] = {}

    def refresh_ui_tree(self):
        """
        Refresh the state of UI elements of the application.

        This method rebuilds the internal cache of UI elements by traversing the application's UI element tree starting from the root UI element.

        Note:
            The IDs of UI elements are not currently deterministic between calls to this method. This is intended to be improved in future versions.
        """
        # TODO: Make UI elements IDs deterministic
        self._ui_elements = {}
        self.root_ui_element.asdict()

    @classmethod
    def from_pid(cls, pid: int) -> Application:
        """
        Create an Application object from a process ID.

        Args:
            pid (int): The process identifier of the application.

        Returns:
            Application: An instance representing the application with the given PID.

        Raises:
            ValueError: If no application with the given PID is found.

        Note:
            This method is not the most efficient way to retrieve an application by PID, as it iterates over all running applications. This may be optimized in future versions.
        """
        # TODO: This is not the most efficient way to do this
        running_applications = get_running_applications()
        app = next((app for app in running_applications if app.pid == pid), None)
        if app is None:
            raise ValueError(f"No application with pid {pid} found")
        return app

    def get_ui_element(self, _id: str) -> UIElement:
        """
        Get a UI element by its ID.

        Args:
            _id (str): The unique ID of the UI element.

        Returns:
            UIElement: The UI element with the specified ID.

        Raises:
            KeyError: If the UI element with the specified ID is not found.

        Note:
            To get up-to-date data, `refresh_ui_tree` must be called to populate the internal cache before calling this method.
        """
        return self._ui_elements[_id]

    def __repr__(self):
        return f"<Application {self.localized_name} {self.executable_url} pid:'{self.pid}'>"

    @property
    def bundle_url(self) -> str:
        """str: The file URL of the application's bundle."""
        return str(self.running_application.bundleURL())

    @property
    def localized_name(self) -> str:
        """str: The localized name of the application."""
        return str(self.running_application.localizedName())

    @property
    def executable_url(self) -> str:
        """str: The file URL of the application's executable."""
        return str(self.running_application.executableURL())

    @classmethod
    def from_menu_bar_owning_app(cls) -> Application:
        """
        Returns the application that owns the currently displayed menu bar.

        Returns:
            Application: An instance representing the application that owns the menu bar.

        Note:
            This method usually returns the frontmost application, same as `from_frontmost_app`, as in macOS the menu bar is generally owned by the active application.
        """
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        return Application(active_app)

    @classmethod
    def from_frontmost_app(cls) -> Application:
        """
        Returns the frontmost application, which is the application that currently receives key events.

        Returns:
            Application: An instance representing the frontmost application.
        """
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        return Application(active_app)

    @property
    def _main_window(self) -> AS.AXUIElementRef:
        """
        AS.AXUIElementRef: The main window of the application as an accessibility element.

        Returns:
            AS.AXUIElementRef: The main window's accessibility element if available, otherwise the application's accessibility element.
        """
        value = AS.AXUIElementCopyAttributeValue(self.application, AS.kAXMainWindowAttribute, None)[1]
        if value is not None:
            return value
        return self.application

    @property
    def root_ui_element(self) -> UIElement:
        """
        UIElement: The root UIElement of the application, representing the main window or the application itself.

        This property provides access to the root of the application's UI element tree, with children lazily loaded as needed.

        Returns:
            UIElement: The root UIElement instance.
        """
        return UIElement(self._main_window, self)


def get_running_applications() -> list[Application]:
    """
    Get a list of all running applications.

    Returns:
        list[Application]: A list of Application instances representing all running applications.
    """
    applications = []
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        applications.append(Application(app))
    return applications
