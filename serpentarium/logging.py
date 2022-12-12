"""
By default, Python's logging library is not safe to use with multiprocessing. Simply logging to a
file or the console can result in messages becoming interleaved or other unexpected behavior. It may
be desirable for plugins to log to the same handler as the host process instead of having their own
log files or output streams. One way of accomplishing this is for plugins to push their log messages
to a queue which is serviced by a single process.
"""

import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Sequence


def configure_child_process_logger(ipc_queue: Queue, level: int = logging.NOTSET):
    """
    Configures a child process to send all log messages to a queue

    This function can be run on a child process to configure it to push all its log messages to a
    queue. Note that formatting of the log messages will be left to the process servicing the queue.
    Additionally, the only filtering performed is based on log level. By default, all log messages
    are pushed to the queue.

    :param ipc_queue: A Queue object shared between the plugin and the queue servicing process
    :param level: The minimum log level of statements to push to the queue; messages below this log
                  level will be dropped, defaults to logging.NOTSET
    """
    root = logging.getLogger()
    root.addHandler(QueueHandler(ipc_queue))
    root.setLevel(level)


def configure_host_process_logger(
    ipc_queue: Queue,
    handlers: Sequence[logging.handlers.QueueHandler] = [],
) -> QueueListener:
    """
    Configures the root logger to use a QueueListener

    A QueueListener can be used to process the log messages from a child process. This function
    configures a QueueListener to use the provided `ipc_queue` and handlers. It configures the root
    logger to push log messages from the host process into the `ipc_queue`. Finally, it returns the
    QueueListener.

    Note that you will need to call `QueueListener.start()`, otherwise the log messages will not be
    processed. See https://docs.python.org/3/library/logging.handlers.html#queuelistener for more
    information about QueueListener

    :param ipc_queue: A Queue shared by the host and child process that stores log messages
    :param handlers: A Sequence of LogHandler objects that the QueueListener will use to handle log
                     messages it pulls off of the ipc_queue

    :return: An unstarted QueueListener object
    """
    root = logging.getLogger()
    root.addHandler(logging.handlers.QueueHandler(ipc_queue))

    return QueueListener(ipc_queue, *handlers, respect_handler_level=True)
