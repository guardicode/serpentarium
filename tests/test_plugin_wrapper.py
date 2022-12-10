from pathlib import Path

import pytest

from serpentarium.plugin_wrapper import PluginWrapper

PLUGIN_DIR = Path(__file__).parent / "plugins"


def test_plugin_isolation():
    plugin1 = PluginWrapper(plugin_name="plugin1", plugin_directory=PLUGIN_DIR / "plugin1")
    plugin2 = PluginWrapper(plugin_name="plugin2", plugin_directory=PLUGIN_DIR / "plugin2")

    assert "Tweedledee" in plugin1.run()
    assert "Tweedledum" in plugin2.run()

    # Run again to ensure plugin2 didn't overwrite plugin1's imports
    assert "Tweedledee" in plugin1.run()
    assert "Tweedledum" in plugin2.run()


def test_module_not_found_incorrect_plugin_name():
    with pytest.raises(ModuleNotFoundError):
        plugin = PluginWrapper(plugin_name="NONEXISTANT", plugin_directory=PLUGIN_DIR / "plugin1")
        plugin.run()
