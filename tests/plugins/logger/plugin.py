import logging
from typing import Iterable, Tuple

from serpentarium import AbstractPlugin

logger = logging.getLogger("LoggingPlugin")


class Plugin(AbstractPlugin):
    def run(self, log_messages: Iterable[Tuple[int, str]] = []):  # type: ignore[override]
        for msg in log_messages:
            logger.log(msg[0], msg[1])
