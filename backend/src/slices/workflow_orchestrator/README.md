# Workflow Orchestrator Slice

This slice introduces declarative workflow orchestration driven by YAML definitions. It is responsible for loading workflow files from disk, validating them against the workflow schema, executing them sequentially with mock agents, and exposing APIs to start and observe runs.

## Responsibilities
- Parse workflow YAML files stored alongside the slice under `workflows/`.
- Validate workflow definitions using the bundled JSON Schema before execution.
- Execute workflow steps in order with built-in mock agents (planner, designer, builder).
- Maintain in-memory run state for active runs and expose polling endpoints.

## Boundaries
- No persistence beyond process memory.
- No external agent calls; all behavior is simulated with deterministic responses.
- No branching, parallelism, or long-running background workers.

## API Entry Points
- `POST /workflow/run` — start a workflow run by name with input values.
- `GET /workflow/run/{run_id}` — poll the status of a workflow run, including step outputs.
- `GET /workflow/definition/{workflow_name}` — retrieve a validated workflow definition for clients.

Refer to `schema.json` for the contract and `workflow_definition.schema.json` for the YAML validation rules.
