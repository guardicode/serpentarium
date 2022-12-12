import os
import sys

assert "wonderland" not in sys.modules

import wonderland  # noqa: E402

from serpentarium import MultiUsePlugin, NamedPluginMixin  # noqa: E402


class Plugin(NamedPluginMixin, MultiUsePlugin):
    def run(self, **kwargs) -> str:
        print(f"I am plugin 1: {os.getpid()}")

        return f"My name is {wonderland.pick_twin()}"
