"""Router for the workflow orchestrator slice."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from importlib import resources
from typing import Any, Literal
from uuid import uuid4

import yaml
from fastapi import APIRouter, HTTPException
from jsonschema import validate
from pydantic import BaseModel

router = APIRouter(prefix="/workflow", tags=["workflow_orchestrator"])


@dataclass
class WorkflowStepDefinition:
    """Step definition parsed from YAML."""

    id: str
    agent: str
    input: str
    name: str | None = None


@dataclass
class WorkflowDefinition:
    """Validated workflow definition."""

    version: str | int
    name: str
    description: str
    inputs: list[dict[str, Any]]
    agents: list[str]
    steps: list[WorkflowStepDefinition]

    def to_contract(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "agents": [{"name": agent, "kind": "mock"} for agent in self.agents],
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "agent": step.agent,
                    "input": step.input,
                }
                for step in self.steps
            ],
        }


@dataclass
class StepRunState:
    """Track the runtime status of a step."""

    id: str
    agent: str
    input: str | None = None
    output: str | None = None
    status: Literal["pending", "running", "completed", "failed"] = "pending"


@dataclass
class RunState:
    """Runtime state for an executing workflow."""

    run_id: str
    workflow_name: str
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    current_step: str | None = None
    error: str | None = None
    inputs: dict[str, str] = field(default_factory=dict)
    steps: list[StepRunState] = field(default_factory=list)


class WorkflowRunRequest(BaseModel):
    """Contract-aligned workflow run request."""

    workflow_name: str
    inputs: dict[str, str]


class WorkflowRunStartResponse(BaseModel):
    """Response containing the issued run identifier."""

    run_id: str
    workflow_name: str


class WorkflowRunStep(BaseModel):
    """Serialized step status for clients."""

    id: str
    agent: str
    input: str | None
    output: str | None
    status: Literal["pending", "running", "completed", "failed"]


class WorkflowRunStatusResponse(BaseModel):
    """Workflow run status payload."""

    run_id: str
    workflow_name: str
    status: Literal["pending", "running", "completed", "failed"]
    current_step: str | None
    steps: list[WorkflowRunStep]
    error: str | None


def _load_contract_schema() -> dict[str, Any]:
    schema_path = resources.files(__package__) / "schema.json"
    with schema_path.open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


def _load_workflow_schema() -> dict[str, Any]:
    schema_path = resources.files(__package__) / "workflow_definition.schema.json"
    with schema_path.open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


_CONTRACT = _load_contract_schema()
_WORKFLOW_SCHEMA = _load_workflow_schema()
_TEMPLATE_PATTERN = re.compile(r"\{\{\s*([^}]+)\s*\}\}")
_MOCK_AGENTS: dict[str, dict[str, Any]] = {
    "planner": {"delay": 0.6, "template": "Planner shaped a path: {input}"},
    "designer": {"delay": 0.8, "template": "Designer framed the experience: {input}"},
    "builder": {"delay": 0.9, "template": "Builder delivered the artifact: {input}"},
}
_WORKFLOWS: dict[str, WorkflowDefinition] = {}
_RUNS: dict[str, RunState] = {}


def _get_response_schema(path: str, method: str) -> dict[str, Any]:
    api_contracts = _CONTRACT.get("contracts", {}).get("api", [])
    for entry in api_contracts:
        if entry.get("method") == method and entry.get("path") == path:
            schema_ref = entry.get("responseSchema", {})
            if "$ref" in schema_ref:
                ref_target = schema_ref["$ref"].split("/")[-1]
                return _CONTRACT.get("$defs", {}).get(ref_target, {})
            return schema_ref
    return {}


def _validate_response(payload: BaseModel | dict[str, Any], path: str, method: str) -> None:
    schema = _get_response_schema(path=path, method=method)
    if not schema:
        raise ValueError(f"Response schema is not defined for {method} {path} in the workflow orchestrator contract.")

    instance = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else payload
    validate(instance=instance, schema=schema)


def _validate_workflow_definition(raw_definition: dict[str, Any]) -> dict[str, Any]:
    validate(instance=raw_definition, schema=_WORKFLOW_SCHEMA)

    declared_agents = {agent.get("name") for agent in raw_definition.get("agents", [])}
    unsupported_agents = [name for name in declared_agents if name not in _MOCK_AGENTS]
    if unsupported_agents:
        raise ValueError(f"Unsupported agent(s) declared: {', '.join(unsupported_agents)}")

    for step in raw_definition.get("steps", []):
        if step.get("agent") not in declared_agents:
            raise ValueError(f"Step {step.get('id')} references unknown agent {step.get('agent')}")
    return raw_definition


def _load_workflows_from_disk() -> dict[str, WorkflowDefinition]:
    definitions: dict[str, WorkflowDefinition] = {}
    workflows_dir = resources.files(__package__) / "workflows"

    for workflow_path in workflows_dir.glob("*.yml"):
        raw_definition = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        validated = _validate_workflow_definition(raw_definition)
        definitions[validated["name"]] = WorkflowDefinition(
            version=validated["version"],
            name=validated["name"],
            description=validated["description"],
            inputs=validated.get("inputs", []),
            agents=[agent["name"] for agent in validated.get("agents", [])],
            steps=[
                WorkflowStepDefinition(
                    id=step["id"],
                    name=step.get("name"),
                    agent=step["agent"],
                    input=step["input"],
                )
                for step in validated.get("steps", [])
            ],
        )

    for workflow_path in workflows_dir.glob("*.yaml"):
        raw_definition = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        validated = _validate_workflow_definition(raw_definition)
        definitions[validated["name"]] = WorkflowDefinition(
            version=validated["version"],
            name=validated["name"],
            description=validated["description"],
            inputs=validated.get("inputs", []),
            agents=[agent["name"] for agent in validated.get("agents", [])],
            steps=[
                WorkflowStepDefinition(
                    id=step["id"],
                    name=step.get("name"),
                    agent=step["agent"],
                    input=step["input"],
                )
                for step in validated.get("steps", [])
            ],
        )

    return definitions


def _resolve_template_value(expression: str, context: dict[str, Any]) -> str:
    parts = expression.split(".")
    value: Any = context
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise ValueError(f"Unable to resolve template variable '{expression}'")
    return str(value)


def _render_template(template: str, context: dict[str, Any]) -> str:
    def replacer(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        return _resolve_template_value(expression, context)

    return _TEMPLATE_PATTERN.sub(replacer, template)


async def _run_mock_agent(agent_name: str, input_text: str) -> str:
    behavior = _MOCK_AGENTS.get(agent_name)
    if behavior is None:
        raise ValueError(f"Agent '{agent_name}' is not supported")

    await asyncio.sleep(behavior.get("delay", 0.5))
    return behavior["template"].format(input=input_text)


def _initialize_run_state(workflow: WorkflowDefinition, inputs: dict[str, str]) -> RunState:
    step_states = [StepRunState(id=step.id, agent=step.agent) for step in workflow.steps]
    return RunState(
        run_id=str(uuid4()),
        workflow_name=workflow.name,
        steps=step_states,
        inputs=inputs,
    )


def _prepare_context(run_state: RunState) -> dict[str, Any]:
    return {
        "inputs": run_state.inputs,
        "steps": {step.id: {"output": step.output} for step in run_state.steps},
    }


async def _execute_run(run_id: str, workflow: WorkflowDefinition) -> None:
    run_state = _RUNS.get(run_id)
    if not run_state:
        return

    run_state.status = "running"

    for index, step_definition in enumerate(workflow.steps):
        run_state.current_step = step_definition.id
        step_state = run_state.steps[index]
        step_state.status = "running"

        try:
            context = _prepare_context(run_state)
            resolved_input = _render_template(step_definition.input, context)
            step_state.input = resolved_input

            output = await _run_mock_agent(step_definition.agent, resolved_input)
            step_state.output = output
            step_state.status = "completed"
        except Exception as exc:  # noqa: BLE001
            step_state.status = "failed"
            run_state.status = "failed"
            run_state.error = str(exc)
            run_state.current_step = None
            return

    run_state.current_step = None
    run_state.status = "completed"


def _serialize_run_state(run_state: RunState) -> WorkflowRunStatusResponse:
    return WorkflowRunStatusResponse(
        run_id=run_state.run_id,
        workflow_name=run_state.workflow_name,
        status=run_state.status,
        current_step=run_state.current_step,
        steps=[
            WorkflowRunStep(
                id=step.id,
                agent=step.agent,
                input=step.input,
                output=step.output,
                status=step.status,
            )
            for step in run_state.steps
        ],
        error=run_state.error,
    )


def _validate_inputs(workflow: WorkflowDefinition, provided: dict[str, str]) -> dict[str, str]:
    normalized_inputs: dict[str, str] = {}
    declared_inputs = {item["name"]: item for item in workflow.inputs}

    for name, definition in declared_inputs.items():
        if definition.get("required", True) and name not in provided:
            raise HTTPException(status_code=400, detail=f"Missing required input: {name}")
        normalized_inputs[name] = provided.get(name, "")

    return normalized_inputs


def _ensure_workflows_loaded() -> None:
    global _WORKFLOWS  # noqa: PLW0603
    if not _WORKFLOWS:
        _WORKFLOWS = _load_workflows_from_disk()


@router.get(
    "/definition/{workflow_name}",
    summary="Retrieve a workflow definition",
    response_model=dict,
)
async def get_workflow_definition(workflow_name: str) -> dict[str, Any]:
    """Return the validated workflow definition by name."""

    _ensure_workflows_loaded()
    workflow = _WORKFLOWS.get(workflow_name)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    definition = workflow.to_contract()
    _validate_response(payload=definition, path="/workflow/definition/{workflow_name}", method="GET")
    return definition


@router.post("/run", summary="Start a workflow run", response_model=WorkflowRunStartResponse)
async def start_workflow_run(request: WorkflowRunRequest) -> WorkflowRunStartResponse:
    """Start executing a workflow by name."""

    _ensure_workflows_loaded()
    workflow = _WORKFLOWS.get(request.workflow_name)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    inputs = _validate_inputs(workflow, request.inputs)
    run_state = _initialize_run_state(workflow, inputs)
    _RUNS[run_state.run_id] = run_state

    asyncio.create_task(_execute_run(run_state.run_id, workflow))

    response = WorkflowRunStartResponse(run_id=run_state.run_id, workflow_name=workflow.name)
    _validate_response(payload=response, path="/workflow/run", method="POST")
    return response


@router.get("/run/{run_id}", summary="Poll workflow run status", response_model=WorkflowRunStatusResponse)
async def get_workflow_run(run_id: str) -> WorkflowRunStatusResponse:
    """Return the latest status for a workflow run."""

    run_state = _RUNS.get(run_id)
    if run_state is None:
        raise HTTPException(status_code=404, detail="Run not found")

    response = _serialize_run_state(run_state)
    _validate_response(payload=response, path="/workflow/run/{run_id}", method="GET")
    return response


# Load workflows once the module is imported to support readiness for the first request.
_ensure_workflows_loaded()
