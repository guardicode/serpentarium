from typing import Any

from typing_extensions import Protocol


class Plugin(Protocol):
    """A protocol for plugins"""

    def run(self, **kwargs) -> Any:
        """Run a plugin with the provided keyword arguments and returns the result"""
        pass

    @property
    def name(self) -> str:
        """A name that identifies this plugin"""
