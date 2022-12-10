from pathlib import Path

import pytest

from serpentarium import PluginLoader

PLUGIN_DIR = Path(__file__).parent / "plugins"


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
