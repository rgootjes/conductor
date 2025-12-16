# Backend Slice Guidelines

These guidelines govern vertical slice design within the FastAPI backend.

## Structure

- Each slice lives in `backend/src/slices/<slice-name>`.
- Include a `README.md` documenting responsibilities, boundaries, and API entry points.
- Include a `schema.json` describing the public API (routes, request/response models, event contracts).

## Composition

- Slices expose a FastAPI router that is composed by the application entry point.
- Avoid importing between slices; use shared infrastructure packages only when formally defined.

## Data and Services

- Keep data access, validation, and business rules scoped to the slice.
- External integrations should be abstracted behind interfaces owned by the slice.

## Evolution

- Version contract changes in `schema.json` and document them in the slice README.
- Favor non-breaking changes; deprecate before removal when possible.
