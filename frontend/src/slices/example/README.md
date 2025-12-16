# Example Slice (Frontend)

This slice demonstrates the expected structure for frontend vertical slices.

## Responsibilities

- Provide a UI entry point that can be mounted by the app shell.
- Define its public contract in `schema.json` for consumption by other slices or tooling.
- Keep internal components, styles, and state within this directory.

## Boundaries

- No direct imports from other slices. Shared utilities must be promoted to an approved shared location before reuse.
- External communication should follow the contract documented in `schema.json`.

## Public Entry Point

- `ExampleEntry` renders placeholder content and can be linked from the app shell. Future functionality should stay within this directory.
