# Frontend Vertical Slices

Each slice is a self-contained feature module. A slice owns its UI entry points, local state management, styling, and schemas describing any outward-facing contracts.

## Rules for Slice Isolation

- Do not import code from other slices directly. Communication should occur through schema-driven contracts or shared platform primitives (e.g., framework utilities) that are explicitly allowed.
- Keep all slice-specific assets (components, hooks, styles, tests) within the slice directory.
- A slice should remain buildable and testable in isolation. Avoid hidden couplings such as shared mutable state.
- Cross-slice knowledge should flow through schemas located in each slice’s `schema.json` file.
- Global app scaffolding (routing, layout) may reference slices by their public entry points but must not depend on their internal details.

## Adding a New Slice

1. Create a new directory under `src/slices/<slice-name>`.
2. Add a `README.md` that documents the slice’s responsibility, boundaries, and any exposed UI entry points.
3. Add a `schema.json` describing the public interface (props, events, data contracts). Use the repository-level `docs/architecture/slice-definition.schema.json` as a guide.
4. Register any app-level routes or navigation from within the slice’s public entry point to avoid leaking internal structure.
