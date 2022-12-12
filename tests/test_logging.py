import logging
import multiprocessing
from functools import partial
from typing import Callable, Iterable, Tuple

from serpentarium.logging import configure_child_process_logger

LOG_MESSAGES = [
    (logging.DEBUG, "log1"),
    (logging.INFO, "log2"),
    (logging.WARNING, "log3"),
    (logging.CRITICAL, "log4"),
]


def run(configure_logger: Callable[[], None], log_messages: Iterable[Tuple[int, str]]):
    configure_logger()
    logger = logging.getLogger()

    for msg in log_messages:
        logger.log(msg[0], msg[1])


def test_child_process_logger__level_notset():
    spawn_context = multiprocessing.get_context("spawn")
    queue = spawn_context.Queue()
    configure_logging_fn = partial(configure_child_process_logger, queue)

    proc = spawn_context.Process(target=run, args=(configure_logging_fn, LOG_MESSAGES))
    proc.start()
    proc.join(0.15)

    assert not queue.empty()
    assert queue.get_nowait().msg == LOG_MESSAGES[0][1]
    assert queue.get_nowait().msg == LOG_MESSAGES[1][1]
    assert queue.get_nowait().msg == LOG_MESSAGES[2][1]
    assert queue.get_nowait().msg == LOG_MESSAGES[3][1]
    assert queue.empty()


def test_child_process_logger__level_warning():
    spawn_context = multiprocessing.get_context("spawn")
    queue = spawn_context.Queue()
    configure_logger_fn = partial(configure_child_process_logger, queue, logging.WARNING)

    proc = spawn_context.Process(target=run, args=(configure_logger_fn, LOG_MESSAGES))
    proc.start()
    proc.join(0.15)

    assert not queue.empty()
    assert queue.get_nowait().msg == LOG_MESSAGES[2][1]
    assert queue.get_nowait().msg == LOG_MESSAGES[3][1]
    assert queue.empty()
