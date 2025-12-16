# Frontend Slice Guidelines

These guidelines govern how vertical slices are structured within the Next.js frontend.

## Structure

- Each slice resides under `frontend/src/slices/<slice-name>`.
- Include a `README.md` documenting responsibilities, boundaries, and public entry points.
- Include a `schema.json` describing the slice’s public interface (props, events, data contracts).

## Composition

- App-level routes may render slice entry points but must avoid depending on internal components.
- Cross-slice communication should occur via contract-driven props or shared platform services defined outside slices.

## Testing and Styling

- Keep tests alongside slice code to preserve locality.
- Encapsulate styles within the slice; avoid global styles unless coordinated.

## Evolution

- Version changes to `schema.json` when contracts evolve.
- Prefer additive changes over breaking ones; document any breaking changes in the slice README.
