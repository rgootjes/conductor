# Conductor Backend

This FastAPI application follows a vertical slice architecture. Each slice owns its routes, models, and services, and exposes a JSON Schema contract.

## Vertical Slice Usage

- Place each feature under `src/slices/<slice-name>`.
- Keep API routers, request/response models, and slice-specific services within the slice directory.
- Describe the slice’s public API in `schema.json` to support discoverability and validation.

## Isolation Rules

- Do not import directly from other slices. Shared behavior should be promoted to an approved shared module before reuse.
- Route registration should be composed in `src/main.py` (or similar top-level module) using each slice’s exported router.
- Slices should be replaceable without affecting others when contracts remain stable.

## Structure

- `src/main.py` — Application entry point and router composition.
- `src/slices/` — Collection of isolated vertical slices. Each slice includes `README.md` and `schema.json` alongside its router and internals.

Run the app locally with `uvicorn main:app --reload` from the `src` directory (ensure dependencies are installed first).
