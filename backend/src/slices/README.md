# Backend Vertical Slices

Each backend slice is responsible for its API surface, domain models, and service orchestration. Slices should not depend directly on each other; integration happens through contracts or shared infrastructure abstractions agreed upon at the architecture level.

## Rules for Slice Isolation

- A slice owns its routers, request/response models, and internal services.
- Do not import code from another slice. Shared utilities must be lifted into an approved shared package before reuse.
- Route registration should occur within the slice and be composed into the application from `main.py` or other top-level modules.
- Keep side effects and I/O localized to the slice boundary to preserve testability and replacement.

## Adding a New Slice

1. Create a new directory under `src/slices/<slice-name>`.
2. Add a `README.md` describing the slice’s responsibility, boundaries, and API entry points.
3. Add a `schema.json` documenting the public API contract for the slice using JSON Schema.
4. Expose a FastAPI router (e.g., `api.py`) and include it from the application composition layer.
