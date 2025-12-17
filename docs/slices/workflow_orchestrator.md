# Workflow Orchestrator (Declarative v1)

This slice introduces YAML-defined workflows that are executed sequentially by mock agents. It intentionally focuses on a small, explicit surface area to support the first version of declarative orchestration.

## Workflow YAML Format
- **version**: Workflow version identifier.
- **name**: Unique workflow name used by clients.
- **description**: Human-readable summary.
- **inputs**: List of input definitions with `name`, optional `description`, `required` flag (default `true`), and optional `example` value.
- **agents**: Declared agents used by steps. Only the built-in mock agents (`planner`, `designer`, `builder`) are supported in v1.
- **steps**: Ordered list of steps. Each step includes `id`, `agent`, optional `name`, and an `input` string. Inputs can reference prior data using `{{ inputs.<name> }}` or `{{ steps.<step-id>.output }}` templating.

Example (`backend/src/slices/workflow_orchestrator/workflows/demo_linear.yaml`):
```yaml
version: 1
name: demo_linear
description: Demonstrates a linear workflow executed by mock planner, designer, and builder agents.
inputs:
  - name: objective
    description: The goal for the workflow to accomplish
    required: true
  - name: audience
    description: Optional target audience for the plan
    required: false
agents:
  - name: planner
    kind: mock
  - name: designer
    kind: mock
  - name: builder
    kind: mock
steps:
  - id: plan
    name: Plan the approach
    agent: planner
    input: "Outline a plan for {{inputs.objective}} targeted at {{inputs.audience}}"
  - id: design
    name: Design the experience
    agent: designer
    input: "Draft a design informed by {{steps.plan.output}}"
  - id: build
    name: Build the delivery
    agent: builder
    input: "Assemble the final output that reflects {{steps.design.output}}"
```

## Execution Model
1. Workflows are loaded from disk and validated against `workflow_definition.schema.json`.
2. A run is started via `POST /workflow/run` with `workflow_name` and input values. Required inputs must be supplied; optional inputs default to empty strings.
3. The orchestrator executes steps sequentially. Each step resolves its input template using provided inputs and previous step outputs, then calls the appropriate mock agent.
4. Run state (status, current step, outputs) is stored in memory only and exposed via `GET /workflow/run/{run_id}`.

## Agents
Built-in mock agents simulate behavior with small delays and deterministic responses:
- **planner**: "Planner shaped a path: {input}"
- **designer**: "Designer framed the experience: {input}"
- **builder**: "Builder delivered the artifact: {input}"

Agents are referenced by name in the YAML and validated during load to prevent unsupported values.

## Out of Scope for v1
- Authentication or persistence of runs beyond process memory.
- Parallel or branching execution paths.
- Background workers or real AI calls.
- YAML editing from the UI (workflows must exist on disk).
