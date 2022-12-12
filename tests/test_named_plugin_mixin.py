from serpentarium import MultiUsePlugin, NamedPluginMixin


class MyPlugin(NamedPluginMixin, MultiUsePlugin):
    def run(self):
        pass


def test_name_property():
    plugin_name = "MyPluginName"
    plugin = MyPlugin(plugin_name=plugin_name)

    assert plugin.name == plugin_name
