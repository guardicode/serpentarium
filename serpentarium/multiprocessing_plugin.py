import logging
import multiprocessing
from threading import current_thread
from typing import Any, Optional

from . import AbstractPlugin, Plugin
from .constants import SERPENTARIUM

logger = logging.getLogger(SERPENTARIUM)


def NOP():
    pass


class MultiprocessingPlugin(AbstractPlugin):
    def __init__(
        self,
        *,
        plugin: Plugin,
        main_thread_name="MainThread",
        daemon=False,
        configure_logging=NOP,
        **kwargs,
    ):
        super().__init__(plugin_name=plugin.name)
        self._plugin = plugin
        self._main_thread_name = main_thread_name
        self._daemon = daemon
        self._configure_logging = configure_logging

        self._multiprocessing_context = multiprocessing.get_context("spawn")
        self._receiver, self._sender = multiprocessing.Pipe(duplex=False)

        self._proc = None
        self._return_value = None

    def run(self, *, timeout: Optional[float] = None, **kwargs) -> Any:
        self.start(**kwargs)
        self.join(timeout)

        return self.return_value

    def start(self, **kwargs):
        self._proc = self._multiprocessing_context.Process(
            name=self.name, daemon=self._daemon, target=self._run, kwargs=kwargs
        )
        self._proc.start()

    def _run(self, **kwargs):
        current_thread().name = self._main_thread_name
        self._configure_logging()

        return_value = self._plugin.run(**kwargs)
        self._sender.send(return_value)

    def join(self, timeout=None):
        self._proc.join(timeout)
        if self.is_alive():
            return

        logger.debug(f"{self.name} exited with code {self._proc.exitcode}")

        self._retrieve_return_value()

    def is_alive(self) -> bool:
        if self._proc is None:
            return False

        return self._proc.is_alive()

    def _retrieve_return_value(self):
        if self._receiver.poll():
            try:
                self._return_value = self._receiver.recv()
                logger.debug(f"{self.name} returned: {self.return_value}")
            except EOFError as err:
                logger.error(f"Error retrieving the return value for {self.name}: {err}")
        else:
            logger.debug(f"{self.name} did not return a value")

    @property
    def return_value(self) -> Any:
        return self._return_value
