import logging
import multiprocessing
from threading import current_thread
from typing import Any, Optional, Union

from . import NamedPluginMixin, PluginThreadName, SingleUsePlugin
from .constants import SERPENTARIUM
from .nop import NOP
from .types import ConfigureLoggerCallback as ConfigureLoggerCallback

logger = logging.getLogger(SERPENTARIUM)


class MultiprocessingPlugin(NamedPluginMixin, SingleUsePlugin):
    """
    A plugin that runs concurrently in a separate process
    """

    def __init__(
        self,
        *,
        plugin: SingleUsePlugin,
        main_thread_name: Union[PluginThreadName, str] = PluginThreadName.DEFAULT,
        daemon: bool = False,
        configure_child_process_logger: ConfigureLoggerCallback = NOP,
        **kwargs,
    ):
        """
        :param plugin: A Plugin to run in a separate process
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
        :param daemon: Whether or not the process should be a daemon process
        :param configure_child_process_logger: A callable that will be run on the child process to
                                               confirgure concurrent logging
        """
        super().__init__(plugin_name=plugin.name)
        self._plugin = plugin
        self._main_thread_name = main_thread_name
        self._daemon = daemon
        self._configure_child_process_logger = configure_child_process_logger

        self._multiprocessing_context = multiprocessing.get_context("spawn")
        self._receiver, self._sender = multiprocessing.Pipe(duplex=False)

        self._proc = None
        self._calling_thread_name = None
        self._return_value = None

    def run(self, *, timeout: Optional[float] = None, **kwargs) -> Any:
        """
        Run a plugin with the provided keyword arguments and returns the result

        When the timeout argument is not present or None, the operation will block until the
        plugin stops.

        :param: A floating-point number of seconds to wait for the plugin to run

        :return: The data that the plugin returned
        """
        self.start(**kwargs)
        self.join(timeout)

        return self.return_value

    def start(self, **kwargs):
        """
        Launch a new process that runs this plugin
        """
        self._calling_thread_name = current_thread().name

        self._proc = self._multiprocessing_context.Process(
            name=self.name, daemon=self._daemon, target=self._run, kwargs=kwargs
        )
        self._proc.start()

    def _run(self, **kwargs):
        self._set_main_thread_name()
        self._configure_child_process_logger()

        return_value = self._plugin.run(**kwargs)
        self._sender.send(return_value)

    def _set_main_thread_name(self):
        if self._main_thread_name == PluginThreadName.DEFAULT:
            # Do nothing, since the process's main thread will be the interpreter's default
            pass
        elif self._main_thread_name == PluginThreadName.CALLING_THREAD:
            current_thread().name = self._calling_thread_name
        else:
            current_thread().name = self._main_thread_name

    def join(self, timeout: Optional[float] = None):
        """
        Wait for this plugin and its parent process to exit

        When the timeout argument is not present or None, the operation will block until the
        plugin stops.

        :param: A floating-point number of seconds to wait for the plugin to run
        """
        if self._proc is None:
            raise AssertionError("can only join a started plugin")

        self._proc.join(timeout)
        if self.is_alive():
            return

        logger.debug(f"{self.name} exited with code {self._proc.exitcode}")

        self._retrieve_return_value()

    def is_alive(self) -> bool:
        """
        Return whether the plugin is alive (process is still running)

        :return: True if the process/plugin is running. False otherwise.
        """
        if self._proc is None:
            return False

        return self._proc.is_alive()

    def _retrieve_return_value(self):
        try:
            if self._receiver.poll():
                self._return_value = self._read_return_value()
            else:
                logger.error(f"{self.name} did not return a value")
        finally:
            logger.debug(f"Closing Pipe to {self.name}")
            self._receiver.close()
            logger.debug(f"Pipe to {self.name} closed")

    def _read_return_value(self) -> Any:
        try:
            return self._receiver.recv()
            logger.debug(f"{self.name} returned: {self.return_value}")
        except EOFError as err:
            logger.error(f"Error retrieving the return value for {self.name}: {err}")

    @property
    def return_value(self) -> Any:
        """
        The return value of the plugin

        This property will be `None` until the plugin finishes running.
        """
        return self._return_value
