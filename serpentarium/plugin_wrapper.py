import contextlib
import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Optional

from . import CLEAN_SYS_MODULES, AbstractPlugin, Plugin
from .constants import VENDOR_DIRECTORY_NAME


class PluginWrapper(AbstractPlugin):
    """
    Wraps a Plugin to make loading and import system manipulation transparent

    Plugins are isolated by manipulating the import system. This needs to be performed just before
    the plugin is run and the import system must be restored to how it was before it was manipulated
    by this component and the plugin.
    """

    def __init__(self, *, plugin_name: str, plugin_directory: Path, **kwargs):
        super().__init__(plugin_name=plugin_name)

        self._plugin_directory = plugin_directory
        self._vendor_directory = self._plugin_directory / VENDOR_DIRECTORY_NAME
        self.plugin: Optional[Plugin] = None

        self._constructor_kwargs = kwargs

    def run(self, **kwargs) -> Any:
        if self.plugin is not None:
            return self.plugin.run(**kwargs)

        with self._plugin_import_context():
            self.plugin = self._load_plugin()
            return self.plugin.run(**kwargs)

    @contextlib.contextmanager
    def _plugin_import_context(self):
        """
        This context manager performs the following:

        1. Save the state of sys.modules
        2. Reset sys.modules to the interpreter's defaults
        3. Configure the import system to import the plugin and its dependencies
        4. yield
        5. Restore the state of the import system.
        """

        host_process_sys_modules = sys.modules.copy()
        PluginWrapper._set_sys_modules(CLEAN_SYS_MODULES)
        # TODO: It's probably cleaner to use a custom meta path finder instead of adding to sys.path
        sys.path = [str(self._plugin_directory.parent), str(self._vendor_directory), *sys.path]

        yield

        sys.path = sys.path[2:]
        PluginWrapper._set_sys_modules(host_process_sys_modules)

    @staticmethod
    def _set_sys_modules(modules: Dict[str, ModuleType]):
        # WARNING: Attempting to set sys.modules like `sys.modules = modules` may cause Python to
        #          fail. See https://docs.python.org/3/library/sys.html#sys.modules
        sys.modules.clear()
        sys.modules.update(modules)

    def _load_plugin(self) -> Plugin:
        plugin_class = importlib.import_module(f"{self.name}.plugin").Plugin
        return plugin_class(plugin_name=self.name, **self._constructor_kwargs)
