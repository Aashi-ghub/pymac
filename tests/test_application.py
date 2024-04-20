import ApplicationServices as AS
import pytest

from py2mac.application import Application, get_running_applications
from py2mac.ui import UIElement


@pytest.mark.parametrize(
    "application",
    [get_running_applications()[0], Application.from_frontmost_app(), Application.from_menu_bar_owning_app()],
)
def test_application(application):
    assert isinstance(application, Application)
    assert isinstance(application.bundle_url, str)
    assert application.bundle_url.startswith("file://")
    assert isinstance(application.pid, int)
    assert isinstance(application.localized_name, str)
    assert isinstance(application.executable_url, str)
    assert application.bundle_url.startswith("file://")
    assert isinstance(application._main_window, AS.AXUIElementRef)
    assert isinstance(application.root_ui_element, UIElement)
