# Example Slice (Backend)

This slice illustrates the expected layout for FastAPI-based vertical slices.

## Responsibilities

- Define its own API router in `api.py`.
- Document its public request/response contracts in `schema.json`.
- Encapsulate any slice-specific services, models, and validation.

## Boundaries

- Do not import from other slices. Promote reusable concerns to a shared module before reuse.
- Compose the router into the application via the top-level `main.py` without leaking internal helpers.

## Public API

- `GET /example/` — Returns a placeholder payload proving the slice is wired into the application.
