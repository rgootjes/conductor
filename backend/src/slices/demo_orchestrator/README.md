# Demo Orchestrator Backend Slice

This slice simulates an orchestrated run of mock agents to showcase the end-to-end flow without invoking real AI services. It exposes endpoints to start a demo run and to poll its progress while agents execute sequentially in-memory.

## Slice Purpose
- Provide `/demo/run` endpoints that start and track a mock orchestration run.
- Simulate three mock agents (planner, designer, builder) with short delays and textual outputs.
- Maintain run state in memory for the lifetime of the process without persistence or background frameworks.

## Architectural Intent
- Contracts are defined in `schema.json` and runtime responses are validated against those schemas.
- All orchestration logic, state, and routing live within this slice to preserve isolation from other slices.
- Execution happens via simple asyncio tasks; no external services or shared global state beyond the slice-owned registry are used.

## Intentionally Excluded
- No authentication, authorization, or environment-specific toggles are applied.
- No durable storage or cross-slice dependencies are introduced.
- No real AI model calls are invoked; outputs are deterministic strings illustrating agent flow.
