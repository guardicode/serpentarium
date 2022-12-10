import sys

assert "wonderland" not in sys.modules

import wonderland  # noqa: E402

from serpentarium import AbstractPlugin  # noqa: E402


class Plugin(AbstractPlugin):
    def run(self, **kwargs) -> str:
        print("I am plugin 2")

        return f"My name is {wonderland.pick_twin()}"
