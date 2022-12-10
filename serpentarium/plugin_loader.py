from pathlib import Path

from . import Plugin
from .plugin_wrapper import PluginWrapper


class PluginLoader:
    """
    Loads plugins from the provided plugin directory
    """

    def __init__(self, plugin_directory: Path):
        """
        :param plugin_directory: The directory where plugins are stored
        """
        self._plugin_directory = plugin_directory

    def load(self, *, plugin_name: str, **kwargs) -> Plugin:
        """
        Load a plugin by name

        :param plugin_name: The name of the plugin (corresponds to the name of the directory where
                            the plugin is stored)
        :param kwargs: Keyword arguments to be passed to the plugin's constructor
        """
        return PluginWrapper(
            plugin_name=plugin_name,
            plugin_directory=self._plugin_directory / plugin_name,
            **kwargs,
        )
