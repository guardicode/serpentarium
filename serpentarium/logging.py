"""
By default, Python's logging library is not safe to use with multiprocessing. Simply logging to a
file or the console can result in messages becoming interleaved or other unexpected behavior. It may
be desirable for plugins to log to the same handler as the host process instead of having their own
log files or output streams. One way of accomplishing this is for plugins to push their log messages
to a queue which is serviced by a single process.
"""

import logging
from logging.handlers import QueueHandler
from queue import Queue


def configure_child_process_logger(logger_queue: Queue, level: int = logging.NOTSET):
    """
    Configures a child process to send all log messages to a queue

    This function can be run on a child process to configure it to push all its log messages to a
    queue. Note that formatting of the log messages will be left to the process servicing the queue.
    Additionally, the only filtering performed is based on log level. By default, all log messages
    are pushed to the queue.

    :param logger_queue: A Queue object shared between the plugin and the queue servicing process
    :param level: The minimum log level of statements to push to the queue; messages below this log
                  level will be dropped, defaults to logging.NOTSET
    """
    root = logging.getLogger()
    root.addHandler(QueueHandler(logger_queue))
    root.setLevel(level)
