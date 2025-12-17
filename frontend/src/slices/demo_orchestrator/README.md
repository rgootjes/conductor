# Demo Orchestrator Frontend Slice

This slice provides an interactive demo page that kicks off the mock orchestrator and streams progress through simple polling. It demonstrates the frontend contract for observing a sequence of simulated agents.

## Slice Purpose
- Render a "Start Demo" control that triggers a backend run via `/api/demo/run`.
- Poll run status until completion, showing the current agent and accumulated outputs.
- Keep all UI, data handling, and contract definitions isolated within the slice.

## Architectural Intent
- The slice exports `DemoOrchestratorPage` as its public entry point for routing.
- Data fetching stays inside the slice with no cross-slice imports or shared mutable state.
- Contracts are captured in `schema.json` to mirror expected run payload shapes from the backend.

## Intentionally Excluded
- No websocket usage or background workers; simple HTTP polling only.
- No authentication or environment branching is applied.
- No advanced styling layers; visuals remain minimal and self-contained.
