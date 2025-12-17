from fastapi import FastAPI

from .slices.registry import register_slices

app = FastAPI(title="Conductor Backend", version="0.1.0")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


register_slices(app)
