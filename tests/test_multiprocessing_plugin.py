import logging
import multiprocessing
import threading

import pytest

from serpentarium import (
    MultiprocessingPlugin,
    MultiUsePlugin,
    NamedPluginMixin,
    SingleUsePlugin,
    concurrency,
)
from tests.logging_utils import assert_queue_equals, get_logger_config_callback
from tests.plugins.logger.plugin import Plugin as LoggerPlugin


class MyPlugin(NamedPluginMixin, MultiUsePlugin):
    def __init__(self, plugin_name: str, value: int):
        super().__init__(plugin_name=plugin_name)
        self._value = value

    def run(self, **_) -> int:
        return self._value


def test_multiprocessing_plugin_return_value():
    plugin_1_value = 99  # red balloons
    plugin_2_value = 50  # ways to leave your lover

    mp_plugin1 = MultiprocessingPlugin(
        plugin=MyPlugin("plugin1", value=plugin_1_value), daemon=True
    )
    mp_plugin2 = MultiprocessingPlugin(
        plugin=MyPlugin("plugin2", value=plugin_2_value), daemon=True
    )

    assert mp_plugin1.run() == plugin_1_value
    assert mp_plugin2.run() == plugin_2_value


BLOCKING_PLUGIN_RETURN_VALUE = 1000  # miles


class BlockingPlugin(NamedPluginMixin, SingleUsePlugin):
    def __init__(self, plugin_name: str, interrupt: concurrency.Event):
        super().__init__(plugin_name=plugin_name)
        self._interrupt = interrupt

    def run(self, **_) -> int:
        self._interrupt.wait()
        return BLOCKING_PLUGIN_RETURN_VALUE


@pytest.fixture
def interrupt() -> concurrency.Event:
    context = multiprocessing.get_context("spawn")
    return context.Event()


@pytest.fixture
def blocking_plugin(interrupt: concurrency.Event):
    return MultiprocessingPlugin(
        plugin=BlockingPlugin(plugin_name="blocking_plugin", interrupt=interrupt), daemon=True
    )


def test_join(interrupt: concurrency.Event, blocking_plugin: MultiprocessingPlugin):
    assert blocking_plugin.return_value is None

    blocking_plugin.start()
    interrupt.set()
    blocking_plugin.join()

    assert not blocking_plugin.is_alive()
    assert blocking_plugin.return_value == BLOCKING_PLUGIN_RETURN_VALUE


def test_join_timeout(interrupt: concurrency.Event, blocking_plugin: MultiprocessingPlugin):
    blocking_plugin.start()
    blocking_plugin.join(0.002)

    assert blocking_plugin.is_alive()
    interrupt.set()
    blocking_plugin.join()


def test_is_alive__process_not_started():
    plugin = MultiprocessingPlugin(plugin=MyPlugin("plugin1", value=0))

    assert not plugin.is_alive()


def test_join__process_not_started():
    plugin = MultiprocessingPlugin(plugin=MyPlugin("plugin1", value=0))

    with pytest.raises(AssertionError):
        assert not plugin.join()


class NoReturnPlugin(NamedPluginMixin, MultiUsePlugin):
    def run(self, **_):
        pass


def test_return_None():
    plugin = MultiprocessingPlugin(plugin=NoReturnPlugin(plugin_name="test"))

    return_value = plugin.run()

    assert return_value is None


class ExceptionPlugin(NamedPluginMixin, MultiUsePlugin):
    def run(self, **_):
        raise Exception()


def test_plugin_raises_exception():
    plugin = MultiprocessingPlugin(plugin=ExceptionPlugin(plugin_name="test"))

    return_value = plugin.run()

    assert return_value is None


class MainThreadNamePlugin(NamedPluginMixin, MultiUsePlugin):
    def run(self, **_):
        return threading.current_thread().name


def test_main_thread_name_set():
    plugin_thread_name = "Sesame"
    plugin = MultiprocessingPlugin(
        plugin=MainThreadNamePlugin(plugin_name="test"), main_thread_name=plugin_thread_name
    )

    return_value = plugin.run()

    assert return_value == plugin_thread_name


LOG_MESSAGES = [
    (logging.DEBUG, "log1"),
    (logging.INFO, "log2"),
    (logging.WARNING, "log3"),
]


def test_child_process_logger_configuration():
    _, ipc_queue, configure_logger_fn = get_logger_config_callback()

    plugin = MultiprocessingPlugin(
        plugin=LoggerPlugin(plugin_name="logger_test"),
        configure_child_process_logger=configure_logger_fn,
    )

    plugin.run(log_messages=LOG_MESSAGES)

    assert_queue_equals(ipc_queue, LOG_MESSAGES)
