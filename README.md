# serpentarium
A Python framework for running plugins with conflicting dependencies

## Description

Coming soon!

## Caveats

- This package is highly experimental
- `import serpentarium` must be the first thing that your code imports so that
  it can save the state of the interpreter's import system before any other
  imports modify it.
- MultiprocessingPlugin only works with the "spawn" method (for now). On Linux,
  you'll need to use a multiprocessing Context object with the "spawn" method
  to generate any Locks, Events, or other synchronization primitives that will
  be passed to a plugin.

## Development
### Pre-commit hooks
`pre-commit install`
