import objc
from AppKit import NSWorkspace
import ApplicationServices as AS
from attr import define


@define
class UIElement:
    _handle: AS.AXUIElementRef

    @property
    def _attribute_names(self):
        error, attributes = AS.AXUIElementCopyAttributeNames(self._handle, None)
        if error != AS.kAXErrorSuccess:
            raise ValueError(f"Error {error} while trying to get attributes")
        return attributes

    def __getitem__(self, name):
        return self._get_attribute(name)

    def __setitem__(self, name, value):
        raise NotImplementedError

    def __delitem__(self, name):
        raise NotImplementedError

    def __iter__(self):
        return iter(self._attribute_names)

    def __len__(self):
        return len(self._attribute_names)

    def __contains__(self, name):
        return name in self._attribute_names

    def __repr__(self):
        return f"<UIElement '{self}'>"

    def __str__(self):
        return self.get(AS.kAXTitleAttribute) or repr(self._handle)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def _get_attribute(self, name):
        err, value = AS.AXUIElementCopyAttributeValue(self._handle, name, None)
        if err != AS.kAXErrorSuccess:
                raise KeyError(f"Error {err} while trying to get attribute {name}")
        return value

    @property
    def _action_names(self) -> list[str]:
        error, actions = AS.AXUIElementCopyActionNames(self._handle, None)
        if error != AS.kAXErrorSuccess:
            raise ValueError(f"Error {error} while trying to get actions")
        return actions

    @property
    def _actions(self) -> dict[str, "UIAction"]:
        return {name: UIAction(name, self._handle) for name in self._action_names}

    def __getattr__(self, item) -> "UIAction":
        if item in self._action_names:
            return UIAction(item, self._handle, self)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __hasattr__(self, item):
        return item in self._action_names

    def __dir__(self):
        return super().__dir__() + self._action_names

    @property
    def children(self) -> list['UIElement']:
        children = self._get_attribute('AXChildren')
        return [UIElement(handle) for handle in children]

    def items(self):
        return [(name, self._get_attribute(name)) for name in self._attribute_names]


@define
class UIAction:
    _name: str
    _handle: AS.AXUIElementRef
    _UIElement: UIElement

    def __call__(self, *args, **kwargs):
        error = AS.AXUIElementPerformAction(self._handle, self._name)
        if error != AS.kAXErrorSuccess:
            raise ValueError(f"Error {error} while trying to perform action {self._name}")

    def __repr__(self):
        return f"<UIAction '{self._name}'>"

class Application:
    def __init__(self, application):
        self.pid = application.processIdentifier()
        self.application = AS.AXUIElementCreateApplication(self.pid)
        self.running_application = application

    def __repr__(self):
        return f"<Application {self.executable_url} pid:'{self.pid}'>"

    @property
    def bundle_url(self):
        return self.running_application.bundleURL()

    @property
    def localized_name(self):
        return self.running_application.localizedName()

    @property
    def executable_url(self):
        return self.running_application.executableURL()

    @classmethod
    def from_active_app(cls):
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        return Application(active_app)

    @property
    def main_window(self):
        if AS.AXUIElementCopyAttributeValue(self.application, AS.kAXMainWindowAttribute, None)[1] is not None:
            return AS.AXUIElementCopyAttributeValue(self.application, AS.kAXMainWindowAttribute, None)[1]
        return self.application

    @property
    def component_tree(self) -> UIElement:
        return UIElement(self.main_window)

    def get_component_tree(self, attributes_whitelist):
        return self._get_component_tree(self.application, attributes_whitelist)

    def _get_component_tree(self, ax_element, attributes_whitelist):
        element = {
            "Attributes": {},
            "Children": []
        }

        element["Attributes"] = self.get_ax_attributes(ax_element, attributes_whitelist)

        # Fetch children elements if they exist
        children = self.get_ax_attribute(ax_element, 'AXChildren')
        if children:
            for child in children:
                element["Children"].append(self._get_component_tree(child, attributes_whitelist))

        return element

def get_running_applications():
    """ Get a list of all running applications """
    applications = []
    for app in NSWorkspace.sharedWorkspace().runningApplications():
        # get pids
        applications.append(Application(app))
    return applications
