# Architecture Rules

This project uses a **Vertical Slice Architecture** across both frontend (Next.js) and backend (Python).

These rules exist to ensure:
- Strong isolation
- Clear ownership
- AI-friendly discoverability
- Safe parallel development by humans and AI agents

All contributors (human or AI) must follow these rules.

---

## Core Principles

1. **Slices over layers**
   - No global services, controllers, or shared utils
   - Functionality lives end-to-end inside a slice

2. **Isolation by default**
   - A slice may not import another slice’s internals
   - Cross-slice interaction happens only via declared contracts

3. **Self-describing slices**
   - Every slice must define:
     - A machine-readable contract (JSON Schema)
     - A human-readable explanation (README)

4. **Removability**
   - A slice should be removable without breaking unrelated slices
   - No hidden coupling or implicit dependencies

---

## What Is a Slice?

A slice represents **one cohesive capability**.

Examples:
- orchestration.run
- agents.execute
- context.store
- ui.goalSubmission
- ui.orchestrationTimeline

A slice owns:
- Its data
- Its logic
- Its public interface

---

## Required Files Per Slice

Every slice MUST contain:
- `slice-name/`
  - `slice.schema.json`
  - `README.md`
  - `index.py` | `index.ts`
  - `internal/`

---

## slice.schema.json (Public Contract)

This file is the **single source of truth** for what the slice exposes.

It defines:
- Public functions or actions
- Input schemas
- Output schemas
- Versioning information

Rules:
- Only what is declared here is public
- Everything else is private
- Other slices may only rely on this contract

---

## README.md (Intent Documentation)

This file explains **why the slice exists**, not how it is implemented.

It must describe:
- Purpose
- Responsibilities
- Non-responsibilities
- Expected evolution

---

## index.py / index.ts (Entry Point)

Rules:
- Only exports declared schema functions
- Function names must match schema keys
- Inputs and outputs must conform exactly to schema
- Validation occurs at the boundary

---

## internal/ (Private Implementation)

Rules:
- Contains all private logic
- Must not be imported by other slices
- Treated as nonexistent outside the slice

---

## Frontend Rules (Next.js)

- Slices live under `frontend/slices/`
- UI, state, server actions belong to the slice
- No shared components folder
- Shared behavior becomes a new slice

---

## Backend Rules (Python)

- Slices live under `backend/slices/`
- API endpoints map directly to slice functions
- Background jobs belong to a slice
- No shared domain services

---

## Cross-Slice Communication

Allowed:
- Calling another slice via its public interface
- Passing schema-compliant data
- Versioned contracts

Forbidden:
- Importing internals
- Shared mutable state
- Implicit coupling

---

## Versioning

- Schemas must declare a version
- Breaking changes require a version bump
- Multiple versions may coexist if needed

---

## Why These Rules Exist

These rules make the system:
- Predictable
- Refactor-friendly
- Discoverable by AI agents
- Safe to extend

Violations introduce hidden coupling and reduce AI effectiveness.

---

## Enforcement

- CI should validate schemas
- Code reviews must enforce slice boundaries
- AI agents must read this document before generating code