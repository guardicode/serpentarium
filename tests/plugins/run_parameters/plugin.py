from typing import Any

from serpentarium import AbstractPlugin


class Plugin(AbstractPlugin):
    def run(self, my_param: Any):  # type: ignore[override]
        return my_param
