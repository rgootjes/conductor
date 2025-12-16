# Backend Architecture Definitions (FastAPI)

This document defines how vertical slices are implemented in the Python backend using FastAPI.

All backend code MUST follow these rules.

---

## Backend Slice Location

All backend slices live under:

backend/slices/

Example:

backend/slices/
- orchestration_run/
- agents_execute/
- context_store/

Each folder represents exactly one slice.

---

## Required Slice Structure

Each backend slice MUST contain:

slice-name/
- slice.schema.json
- README.md
- index.py
- internal/

---

## FastAPI Integration Model

### Core Rule

Slices do NOT define FastAPI routers directly.

Instead:
- Each slice exposes pure Python functions in index.py
- A central API bootstrap layer binds slices to HTTP routes

This prevents:
- Framework leakage
- Cross-slice coupling
- Inconsistent routing patterns

---

## index.py Rules

- Only functions declared in slice.schema.json may exist here
- No FastAPI decorators in slice code
- Functions must be synchronous or async, but explicit
- Inputs and outputs must match schema exactly

Example:

async def run(input: dict) -> dict:
    ...

---

## API Binding Layer

A central module (for example: backend/api/router.py) is responsible for:

- Discovering slices
- Reading slice.schema.json
- Registering FastAPI routes dynamically
- Validating input and output against schema

Slices never import FastAPI directly.

---

## Endpoint Mapping Rules

Default mapping:

- URL path: /api/{slice-name}/{action}
- HTTP method: POST
- Request body: schema input
- Response body: schema output

Example:

Slice: orchestration.run  
Action: run  

POST /api/orchestration/run

---

## Validation Rules

- Input validation happens at the API boundary
- Output validation happens before returning a response
- JSON Schema is the source of truth
- Pydantic models may be generated automatically

---

## internal/ Rules

- Contains all private domain logic
- May include adapters, persistence, and AI calls
- Must not import other slices
- Must not expose public APIs

---

## Dependency Rules

Allowed:
- Python standard library
- Explicit third-party libraries
- Internal modules within the same slice

Forbidden:
- Importing other slices’ internal code
- Shared domain services
- Implicit global state

---

## Background Tasks

- Background tasks belong to a slice
- FastAPI background execution is triggered by the API layer
- Long-running orchestration should be asynchronous

---

## Why This Design Exists

This design ensures:
- Slices are framework-agnostic
- APIs are consistent and discoverable
- AI agents can modify slices safely
- Backend architecture remains evolvable
