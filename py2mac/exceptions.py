class Py2MacError(Exception):
    """
    Base exception class for all Py2Mac-related errors.
    """

    pass


class UIAttributeAccessError(Py2MacError):
    """
    Exception raised when an error occurs while accessing a UI attribute.
    """

    pass


class UIActionError(Py2MacError):
    """
    Exception raised when an error occurs while performing a UI action.

    This exception is typically raised when an action on a UIElement fails,
    such as when the UIElement does not support the action, the action is invalid,
    or due to insufficient accessibility permissions.

    Example::

        try:
            ui_element.perform_action('AXPress')
        except UIActionError as e:
            print(f"Failed to perform action: {e}")

    """

    pass
