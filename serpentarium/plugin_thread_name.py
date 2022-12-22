from enum import Enum, auto


class PluginThreadName(Enum):
    DEFAULT = auto()
    CALLING_THREAD = auto()
