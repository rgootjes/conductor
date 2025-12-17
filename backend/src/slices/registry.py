"""Slice registration for the backend application."""

from fastapi import FastAPI

from .demo_orchestrator import router as demo_orchestrator_router
from .demo_status import router as demo_status_router
from .example.api import router as example_router


def register_slices(app: FastAPI) -> None:
    """Mount all slice routers onto the FastAPI application."""

    app.include_router(example_router, prefix="/example", tags=["example"])
    app.include_router(demo_orchestrator_router)
    app.include_router(demo_status_router)
