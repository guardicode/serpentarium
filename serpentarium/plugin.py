from typing import Any

from typing_extensions import Protocol


class SingleUsePlugin(Protocol):
    """A protocol for a plugin that can be run only once"""

    def run(self, **kwargs) -> Any:
        """
        Run a plugin with the provided keyword arguments and returns the result

        A SingleUsePlugin's run() method can be called once and only once. After the plugin's run()
        method returns, the plugin object should be discarded.
        """
        pass

    @property
    def name(self) -> str:
        """A name that identifies this plugin"""


class MultiUsePlugin(SingleUsePlugin, Protocol):
    """A protocol for plugins"""

    def run(self, **kwargs) -> Any:
        """
        Run a plugin with the provided keyword arguments and returns the result

        Unlike a SingleUsePlugin, a MultiUsePlugin's run() method can be called repeatedly with no
        ill effects.
        """
        pass

    @property
    def name(self) -> str:
        """A name that identifies this plugin"""
