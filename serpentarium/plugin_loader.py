from pathlib import Path
from typing import Optional

from . import MultiprocessingPlugin, MultiUsePlugin
from .nop import NOP
from .plugin_wrapper import PluginWrapper
from .types import ConfigureLoggerCallback as ConfigureLoggerCallback


class PluginLoader:
    """
    Loads plugins from the provided plugin directory
    """

    def __init__(
        self, plugin_directory: Path, configure_child_process_logger: ConfigureLoggerCallback = NOP
    ):
        """
        :param plugin_directory: The directory where plugins are stored
        :param configure_child_process_logger: A callback to configure logging that will be run
                                               by any MultiprocessingPlugin that this object loads.
                                               This can be overridden on each call to
                                               load_multiprocessing_plugin(). Defaults to a NOP.
        """
        self._plugin_directory = plugin_directory
        self._configure_child_process_logger = configure_child_process_logger

    def load(self, *, plugin_name: str, **kwargs) -> MultiUsePlugin:
        """
        Load a plugin by name

        :param plugin_name: The name of the plugin (corresponds to the name of the directory where
                            the plugin is stored)
        :param kwargs: Keyword arguments to be passed to the plugin's constructor

        :return: A MultiUsePlugin
        """
        return PluginWrapper(
            plugin_name=plugin_name,
            plugin_directory=self._plugin_directory / plugin_name,
            **kwargs,
        )

    def load_multiprocessing_plugin(
        self,
        *,
        plugin_name: str,
        main_thread_name: str = "MainThread",
        configure_child_process_logger: Optional[ConfigureLoggerCallback] = None,
        **kwargs,
    ) -> MultiprocessingPlugin:
        """
        Load a MultiprocessingPlugin by name

        :param plugin_name: The name of the plugin (corresponds to the name of the directory where
                            the plugin is stored)
        :param main_thread_name: The desired name of the child process's main thread. This is useful
                                 when analyzing logs for applications that are both multi-threaded
                                 and use MultiprocessingPlugins, defaults to "MainThread"
        :param configure_child_process_logger: A callback to configure logging on the child process.
                                               This overrides the callback provided to the
                                               constructor. Defaults to `None`
        :param kwargs: Keyword arguments to be passed to the plugin's constructor

        :return: A MultiprocessingPlugin
        """

        plugin = PluginWrapper(
            plugin_name=plugin_name,
            plugin_directory=self._plugin_directory / plugin_name,
            **kwargs,
        )

        if configure_child_process_logger is None:
            configure_logger_fn = self._configure_child_process_logger
        else:
            configure_logger_fn = configure_child_process_logger

        return MultiprocessingPlugin(
            plugin=plugin,
            main_thread_name=main_thread_name,
            configure_child_process_logger=configure_logger_fn,
            **kwargs,
        )
