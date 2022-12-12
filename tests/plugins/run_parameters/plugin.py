from typing import Any

from serpentarium import MultiUsePlugin, NamedPluginMixin


class Plugin(NamedPluginMixin, MultiUsePlugin):
    def run(self, my_param: Any):  # type: ignore[override]
        return my_param
