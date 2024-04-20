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
This module provides various utility functions.
"""

import objc


def check_access() -> bool:
    """
    Check if the current process has accessibility permissions.

    This function determines whether the application is trusted to use the Accessibility API.
    If the application is not trusted, it will prompt the user to grant access.

    Returns:
        bool: True if the process is trusted with accessibility permissions, False otherwise.

    Notes:
        - This function uses the `AXIsProcessTrustedWithOptions` function from the ApplicationServices framework.
        - The `options` dictionary includes `AXTrustedCheckOptionPrompt: True` to enable prompting.
        - If the application is not trusted, macOS will display a prompt requesting accessibility permissions.

    Example:
        >>> if not check_access():
        ...     print("Accessibility permissions are required.")
    """
    # Load the ApplicationServices framework
    AS = objc.loadBundle("CoreServices", globals(), "/System/Library/Frameworks/ApplicationServices.framework")
    # Load the AXIsProcessTrustedWithOptions function
    objc.loadBundleFunctions(AS, globals(), [("AXIsProcessTrustedWithOptions", b"Z@")])
    # Set options to prompt the user if not already trusted
    options = {"AXTrustedCheckOptionPrompt": True}
    # Call the function to check if the process is trusted
    return AXIsProcessTrustedWithOptions(options)  # type: ignore  # noqa: F821
