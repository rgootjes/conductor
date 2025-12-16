# Frontend Architecture Definitions (Next.js)

This document defines how vertical slices are implemented in the Next.js frontend.

All frontend code MUST follow these rules.

---

## Frontend Slice Location

All frontend slices live under:

frontend/slices/

Example:

frontend/slices/
- goal-submission/
- orchestration-timeline/
- agent-inspector/

Each folder represents exactly one slice.

---

## Required Slice Structure

Each frontend slice MUST contain:

slice-name/
- slice.schema.json
- README.md
- index.ts
- components/
- internal/

---

## index.ts Rules

- Acts as the public entry point for the slice
- Only exports declared in slice.schema.json
- No default exports
- No UI components exported directly unless declared

Example:

export async function submitGoal(input: SubmitGoalInput): Promise<SubmitGoalOutput> {
  ...
}

---

## UI Component Rules

- Components live inside the slice
- No global shared components directory
- Shared UI behavior becomes a new slice
- Styling is owned by the slice

---

## Server Actions and Data Fetching

Rules:
- Server actions belong to the slice
- Backend API calls are encapsulated inside the slice
- Other slices must not call backend APIs directly

This keeps network boundaries explicit and enforceable.

---

## slice.schema.json (Frontend)

Frontend schemas define:
- Public UI actions
- Input data (user intent, UI state)
- Output data (events, state changes)

Frontend schemas may mirror backend schemas but are not required to match exactly.

---

## Cross-Slice Interaction

Allowed:
- Calling another slice via its index.ts exports
- Passing schema-compliant data
- Event-based communication declared in schema

Forbidden:
- Importing UI components from another slice
- Accessing another slice’s internal folder
- Global UI state shared implicitly

---

## State Management Rules

- State is local to the slice
- No global Redux, Zustand, or shared stores
- Cross-slice state must be explicit via contracts
- Persistent state lives in backend slices

---

## Routing Rules (App Router)

- Pages are thin composition layers
- Pages import slices, not business logic
- Routing files contain no domain logic

Example:

import { GoalSubmission } from "@/slices/goal-submission";

export default function Page() {
  return <GoalSubmission />;
}

---

## Why This Design Exists

This design ensures:
- UI capabilities are modular
- Slices are independently removable
- AI can reason about UI behavior in isolation
- Frontend and backend evolve independently
