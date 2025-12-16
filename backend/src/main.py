from fastapi import FastAPI

from slices.example.api import router as example_router

app = FastAPI(title="Conductor Backend", version="0.1.0")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(example_router, prefix="/example", tags=["example"])
