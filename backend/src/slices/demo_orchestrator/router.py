"""Router for the demo orchestrator slice."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from importlib import resources
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from jsonschema import validate
from pydantic import BaseModel

router = APIRouter(prefix="/demo", tags=["demo_orchestrator"])


@dataclass
class _StepState:
    agent: str
    status: str = "pending"
    output: str | None = None


@dataclass
class _RunState:
    run_id: str
    status: str = "pending"
    current_agent: str | None = None
    steps: list[_StepState] = field(default_factory=list)


_RUNS: dict[str, _RunState] = {}

_AGENT_SEQUENCE: list[tuple[str, str]] = [
    ("planner", "Planner mapped the execution steps for the demo."),
    ("designer", "Designer outlined the UI experience for the mock agents."),
    ("builder", "Builder assembled the simulated outputs for the flow."),
]

_AGENT_DELAYS: list[float] = [1.0, 1.4, 1.1]


class DemoRunStartResponse(BaseModel):
    """Contract-aligned response when starting a run."""

    run_id: str


class DemoRunStep(BaseModel):
    """Representation of an agent step within a run."""

    agent: Literal["planner", "designer", "builder"]
    status: Literal["pending", "running", "completed"]
    output: str | None = None


class DemoRunStatusResponse(BaseModel):
    """Contract-aligned run status payload."""

    run_id: str
    status: Literal["pending", "running", "completed"]
    current_agent: str | None
    steps: list[DemoRunStep]


def _load_contract_schema() -> dict[str, Any]:
    schema_path = resources.files(__package__) / "schema.json"
    with schema_path.open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


_CONTRACT = _load_contract_schema()


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


def _validate_response(payload: BaseModel, path: str, method: str) -> None:
    schema = _get_response_schema(path=path, method=method)
    if not schema:
        raise ValueError(f"Response schema is not defined for {method} {path} in the demo orchestrator contract.")

    validate(instance=payload.model_dump(mode="json"), schema=schema)


def _initialize_run_state(run_id: str) -> _RunState:
    return _RunState(
        run_id=run_id,
        status="pending",
        current_agent=None,
        steps=[_StepState(agent=agent) for agent, _ in _AGENT_SEQUENCE],
    )


async def _execute_run(run_id: str) -> None:
    run_state = _RUNS.get(run_id)
    if not run_state:
        return

    run_state.status = "running"

    for index, (agent, output_text) in enumerate(_AGENT_SEQUENCE):
        step = run_state.steps[index]
        run_state.current_agent = agent
        step.status = "running"

        await asyncio.sleep(_AGENT_DELAYS[index])

        step.output = output_text
        step.status = "completed"

    run_state.current_agent = None
    run_state.status = "completed"


def _serialize_run_state(run_state: _RunState) -> DemoRunStatusResponse:
    return DemoRunStatusResponse(
        run_id=run_state.run_id,
        status=run_state.status,
        current_agent=run_state.current_agent,
        steps=[
            DemoRunStep(agent=step.agent, status=step.status, output=step.output)
            for step in run_state.steps
        ],
    )


@router.post("/run", summary="Start a new demo orchestration run", response_model=DemoRunStartResponse)
async def start_demo_run() -> DemoRunStartResponse:
    """Start a new simulated demo orchestration run."""

    run_id = str(uuid4())
    run_state = _initialize_run_state(run_id)
    _RUNS[run_id] = run_state

    asyncio.create_task(_execute_run(run_id))

    response = DemoRunStartResponse(run_id=run_id)
    _validate_response(payload=response, path="/demo/run", method="POST")
    return response


@router.get(
    "/run/{run_id}",
    summary="Poll the status of a demo orchestration run",
    response_model=DemoRunStatusResponse,
)
async def get_demo_run(run_id: str) -> DemoRunStatusResponse:
    """Retrieve the latest status for a simulated demo orchestration run."""

    run_state = _RUNS.get(run_id)
    if run_state is None:
        raise HTTPException(status_code=404, detail="Run not found")

    response = _serialize_run_state(run_state)
    _validate_response(payload=response, path="/demo/run/{run_id}", method="GET")
    return response
