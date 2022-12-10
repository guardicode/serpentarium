from abc import ABC, abstractmethod
from typing import Any

from . import Plugin


class AbstractPlugin(ABC, Plugin):
    def __init__(self, *, plugin_name: str, **kwargs):
        self._plugin_name = plugin_name

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass

    @property
    def name(self) -> str:
        return self._plugin_name
