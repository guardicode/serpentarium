import logging
import multiprocessing
import multiprocessing.context
from functools import partial
from typing import Tuple

from serpentarium.logging import configure_child_process_logger
from serpentarium.types import ConfigureLoggerCallback


def get_logger_config_callback(
    log_level=logging.NOTSET,
) -> Tuple[multiprocessing.context.SpawnContext, multiprocessing.Queue, ConfigureLoggerCallback]:
    spawn_context = multiprocessing.get_context("spawn")
    ipc_queue = spawn_context.Queue()
    configure_logger_fn = partial(configure_child_process_logger, ipc_queue, log_level)

    return (spawn_context, ipc_queue, configure_logger_fn)
