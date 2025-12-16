# Conductor Frontend

This Next.js (App Router) application uses a vertical slice architecture. Each slice is self-contained and represents a feature boundary.

## Vertical Slice Usage

- Place each feature under `src/slices/<slice-name>`.
- Keep UI components, styles, hooks, and slice-specific utilities within the slice directory.
- Define the slice contract in `schema.json` to describe props, events, and external data expectations.

## Isolation Rules

- Do not import code from other slices directly. Interactions should happen through documented schemas or platform-level primitives.
- Avoid shared mutable state across slices. Cross-cutting concerns should be promoted to well-defined shared modules before reuse.
- App-level routing can mount slice entry points, but internal slice details must remain encapsulated.

## Structure

- `src/app/` — App Router entry points, layouts, and global styling.
- `src/slices/` — Collection of isolated vertical slices. Each slice includes its own `README.md` and `schema.json`.

Run the app locally with `npm install` followed by `npm run dev`.
