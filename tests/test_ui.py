from pprint import pprint

from py2mac.application import Application
from py2mac.ui import UIElement


def test_ui():
    application = Application.from_frontmost_app()
    root_ui_element = application.root_ui_element
    assert isinstance(root_ui_element, UIElement)
    assert isinstance(root_ui_element.actions, list)
    assert isinstance(root_ui_element.children, list)
    assert isinstance(root_ui_element.children[0], UIElement)


def test_tree_to_dict():
    application = Application.from_frontmost_app()
    root_ui_element = application.root_ui_element
    tree = root_ui_element.asdict()

    assert isinstance(tree, dict)
    assert "children" in tree
    assert isinstance(tree["children"], list)
    pprint(tree)
