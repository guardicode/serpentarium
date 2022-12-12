import logging
import logging.handlers
import multiprocessing
from functools import partial
from queue import Queue
from typing import Callable, Iterable, Tuple

from serpentarium.logging import configure_child_process_logger, configure_host_process_logger

LOG_MESSAGES = [
    (logging.DEBUG, "log1"),
    (logging.INFO, "log2"),
    (logging.WARNING, "log3"),
    (logging.CRITICAL, "log4"),
]


def run(configure_logger: Callable[[], None], messages_to_log: Iterable[Tuple[int, str]]):
    configure_logger()
    log_messages(messages_to_log)


def log_messages(messages_to_log: Iterable[Tuple[int, str]]):
    logger = logging.getLogger()

    for msg in messages_to_log:
        logger.log(msg[0], msg[1])


def test_child_process_logger__level_notset():
    spawn_context = multiprocessing.get_context("spawn")
    ipc_queue = spawn_context.Queue()
    configure_logging_fn = partial(configure_child_process_logger, ipc_queue)

    proc = spawn_context.Process(target=run, args=(configure_logging_fn, LOG_MESSAGES))
    proc.start()
    proc.join(0.15)

    assert not ipc_queue.empty()
    assert ipc_queue.get_nowait().msg == LOG_MESSAGES[0][1]
    assert ipc_queue.get_nowait().msg == LOG_MESSAGES[1][1]
    assert ipc_queue.get_nowait().msg == LOG_MESSAGES[2][1]
    assert ipc_queue.get_nowait().msg == LOG_MESSAGES[3][1]
    assert ipc_queue.empty()


def test_child_process_logger__level_warning():
    spawn_context = multiprocessing.get_context("spawn")
    ipc_queue = spawn_context.Queue()
    configure_logger_fn = partial(configure_child_process_logger, ipc_queue, logging.WARNING)

    proc = spawn_context.Process(target=run, args=(configure_logger_fn, LOG_MESSAGES))
    proc.start()
    proc.join(0.15)

    assert not ipc_queue.empty()
    assert ipc_queue.get_nowait().msg == LOG_MESSAGES[2][1]
    assert ipc_queue.get_nowait().msg == LOG_MESSAGES[3][1]
    assert ipc_queue.empty()


def test_configure_queue_listener():
    ipc_queue = Queue()
    test_queue = Queue()
    test_queue_handler = logging.handlers.QueueHandler(test_queue)
    test_queue_handler.setLevel(logging.INFO)

    queue_listener = configure_host_process_logger(
        ipc_queue=ipc_queue, handlers=[test_queue_handler]
    )

    try:
        queue_listener.start()
        log_messages(LOG_MESSAGES)
    finally:
        queue_listener.stop()

        assert not test_queue.empty()
        assert test_queue.get_nowait().msg == LOG_MESSAGES[1][1]
        assert test_queue.get_nowait().msg == LOG_MESSAGES[2][1]
        assert test_queue.get_nowait().msg == LOG_MESSAGES[3][1]
        assert test_queue.empty()