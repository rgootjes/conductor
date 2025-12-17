"""Router for the demo_status slice."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib import resources
from typing import Any

from fastapi import APIRouter
from jsonschema import validate
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/demo", tags=["demo_status"])


class DemoStatusResponse(BaseModel):
    """Contract-aligned response payload for demo status."""

    status: str
    environment: str
    timestamp: datetime

    model_config = ConfigDict(json_encoders={datetime: lambda value: value.isoformat()})


def _load_contract_schema() -> dict[str, Any]:
    schema_path = resources.files(__package__) / "schema.json"
    with schema_path.open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


_CONTRACT = _load_contract_schema()


def _extract_response_schema(contract: dict[str, Any]) -> dict[str, Any]:
    api_contracts = contract.get("contracts", {}).get("api", [])
    if not api_contracts:
        return {}

    schema_ref = api_contracts[0].get("responseSchema", {})
    if "$ref" in schema_ref:
        ref_target = schema_ref["$ref"].split("/")[-1]
        return contract.get("$defs", {}).get(ref_target, {})

    return schema_ref


_RESPONSE_SCHEMA = _extract_response_schema(_CONTRACT)


def _validate_response(payload: DemoStatusResponse) -> None:
    if not _RESPONSE_SCHEMA:
        raise ValueError("Response schema is not defined in the demo_status contract.")

    validate(instance=payload.model_dump(mode="json"), schema=_RESPONSE_SCHEMA)


@router.get("/status", summary="Retrieve the current demo environment status", response_model=DemoStatusResponse)
async def get_demo_status() -> DemoStatusResponse:
    """Return status information about the running demo environment."""

    payload = DemoStatusResponse(
        status="online",
        environment="local",
        timestamp=datetime.now(timezone.utc),
    )

    _validate_response(payload)
    return payload
