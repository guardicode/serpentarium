from pathlib import Path
from typing import Optional, Union

from . import MultiprocessingPlugin, MultiUsePlugin, PluginThreadName
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

    def load(
        self, *, plugin_name: str, reset_modules_cache: bool = True, **kwargs
    ) -> MultiUsePlugin:
        """
        Load a plugin by name

        Reseting `sys.modules` does not work properly if extension modules have been loaded. The
        `reset_modules_cache` option gives the caller the ability to disable this behavior.

        :param plugin_name: The name of the plugin (corresponds to the name of the directory where
                            the plugin is stored)
        :param reset_modules_cache: Whether or not to reset the `sys.modules` cache to system
                                    defaults before executing the plugin. Setting this to `False`
                                    will break plugin isolation for these plugins. Defaults to
                                    `True`.
        :param kwargs: Keyword arguments to be passed to the plugin's constructor

        :return: A MultiUsePlugin
        """
        return PluginWrapper(
            plugin_name=plugin_name,
            plugin_directory=self._plugin_directory / plugin_name,
            reset_modules_cache=reset_modules_cache,
            **kwargs,
        )

    def load_multiprocessing_plugin(
        self,
        *,
        plugin_name: str,
        main_thread_name: Union[PluginThreadName, str] = PluginThreadName.DEFAULT,
        configure_child_process_logger: Optional[ConfigureLoggerCallback] = None,
        reset_modules_cache=True,
        **kwargs,
    ) -> MultiprocessingPlugin:
        """
        Load a MultiprocessingPlugin by name

        Reseting `sys.modules` does not work properly if extension modules have been loaded. The
        `reset_modules_cache` option gives the caller the ability to disable this behavior.

        :param plugin_name: The name of the plugin (corresponds to the name of the directory where
                            the plugin is stored)
        :param main_thread_name: The name of the child process's main thread. This can either be a
                                 `PluginThreadName` or a string. If it is
                                 `PluginThreadName.DEFAULT`, then child process's main thread will
                                 be whatever the interpreter's default main thread name is. If it is
                                 `PluginThreadName.CALLING_THREAD`, then the child process's main
                                 thread name will match the name of the thread that calls `run()` on
                                 this plugin. If it is a string, the child process's main thread
                                 name will be set to the string value.

                                 Setting this is useful when analyzing logs for applications that
                                 are both multi-threaded and use `MultiprocessingPlugins`, defaults
                                 to `PluginThreadName.DEFAULT`.
        :param configure_child_process_logger: A callback to configure logging on the child process.
                                               This overrides the callback provided to the
                                               constructor. Defaults to `None`
        :param reset_modules_cache: Whether or not to reset the `sys.modules` cache to system
                                    defaults before executing the plugin. Setting this to `False`
                                    will have little to no effect in most cases since
                                    `MultiprocessingPlugins` use the "spawn" method. Defaults to
                                    `True`.
        :param kwargs: Keyword arguments to be passed to the plugin's constructor

        :return: A MultiprocessingPlugin
        """
        plugin = PluginWrapper(
            plugin_name=plugin_name,
            plugin_directory=self._plugin_directory / plugin_name,
            reset_modules_cache=reset_modules_cache,
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
