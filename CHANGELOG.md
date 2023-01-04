# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
the [PEP 440 version scheme](https://peps.python.org/pep-0440/#version-scheme).

## [v0.6.0] - 2023-01-04
## Fixed
- Incorrect type hint for serpentarium.logging.configure_host_process_logger()


## [v0.5.0] - 2022-12-22
### Added
- `PluginThreadName` enum
### Changed
- `main_thread_name` parameter to accept `Union[PluginThreadName|str]`


## [v0.4.0] - 2022-12-21
### Added
- `reset_modules_cache` option to `PluginLoader.load()`
- `reset_modules_cache` option to `PluginLoader.load_multiprocessing_plugin()`


## [v0.3.0] - 2022-12-14
### Added
- serpentarium.types
- serpentarium.types.ConfigureLoggerCallback

### Changed
- Logger configuration callback can be passed to `PluginLoader's` constructor
  and overridden by `PluginLoader.load_multiprocessing_plugin()`

### Fixed
- Explicitly close `MultiprocessingPlugin._receiver()` when done


## [v0.2.0] - 2022-12-12
### Added
- py.typed
- serpentarium.logging
- Missing docstrings in MultiprocessingPlugin

### Changed
- AbstractPlugin to NamedPluginMixin
- MultiprocesingPlugin's configure_logging parameter to configure_child_process_logger
- PluginLoader returns a MultiUsePlugin
- MultiprocessingPlugin is a SingleUsePlugin

### Fixed
- The Alpha status classifier
- MultiprocessingPlugin's violation of the Liskov Substitution Principle


## [v0.1.0] - 2022-12-10
### Added
- README.md
- CHANGELOG.md
- LICENSE.md
- .gitignore for Python
- pre-commit hooks
- pyproject.toml
- dependencies with poetry
- Plugin
- AbstractPlugin
- MultiprocessingPlugin
- PluginLoader
- Event concurrency Protocol
- Lock concurrency Protocol
