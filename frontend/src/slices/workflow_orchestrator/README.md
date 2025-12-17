# Workflow Orchestrator Slice (Frontend)

This slice provides a minimal UI for running declarative workflows backed by the workflow orchestrator API. It surfaces the active workflow metadata, collects required inputs, and displays live progress as the backend executes each mock agent.

## Responsibilities
- Fetch workflow definition metadata for the configured workflow.
- Collect input values and trigger `/workflow/run` through the frontend API proxy.
- Poll `/workflow/run/{run_id}` until completion and render step outputs.

## Boundaries
- No YAML editing or persistence is exposed from the UI.
- Styling remains minimal to keep focus on contract-first behavior.
- Only linear execution is represented; no branching or parallel visualizations.

## Entry Points
- `WorkflowOrchestratorPage` component rendered at `/workflow/orchestrator`.
- API proxy handlers under `/app/api/workflow/*` for backend communication.

Refer to `schema.json` for the UI contract definition.
