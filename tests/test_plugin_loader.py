from pathlib import Path

import pytest

from serpentarium import PluginLoader

PLUGIN_DIR = Path(__file__).parent / "plugins"
MY_PARAM = "test_param"


@pytest.fixture
def plugin_loader() -> PluginLoader:
    return PluginLoader(PLUGIN_DIR)


def test_plugin_isolation(plugin_loader: PluginLoader):
    plugin1 = plugin_loader.load(plugin_name="plugin1")
    plugin2 = plugin_loader.load(plugin_name="plugin2")

    assert "Tweedledee" in plugin1.run()
    assert "Tweedledum" in plugin2.run()

    # Run again to ensure plugin2 didn't overwrite plugin1's imports
    assert "Tweedledee" in plugin1.run()
    assert "Tweedledum" in plugin2.run()


def test_module_not_found_incorrect_plugin_name(plugin_loader: PluginLoader):
    with pytest.raises(ModuleNotFoundError):
        plugin = plugin_loader.load(plugin_name="NONEXISTANT")
        plugin.run()


def test_constructor_parameters(plugin_loader: PluginLoader):
    plugin1 = plugin_loader.load(plugin_name="constructor_parameters", my_param=MY_PARAM)

    return_value = plugin1.run()

    assert return_value == MY_PARAM


def test_run_parameters(plugin_loader: PluginLoader):
    plugin1 = plugin_loader.load(plugin_name="run_parameters")

    return_value = plugin1.run(my_param=MY_PARAM)

    assert return_value == MY_PARAM
