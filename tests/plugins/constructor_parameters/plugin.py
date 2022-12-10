from typing import Any

from serpentarium import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, plugin_name: str, my_param: Any):
        super().__init__(plugin_name=plugin_name)
        self.my_param = my_param

    def run(self, **_):
        return self.my_param
