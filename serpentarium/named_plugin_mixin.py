class NamedPluginMixin:
    def __init__(self, *, plugin_name: str, **kwargs):
        self._plugin_name = plugin_name

    @property
    def name(self) -> str:
        return self._plugin_name
