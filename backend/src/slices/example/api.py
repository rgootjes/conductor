from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Example slice placeholder")
async def get_example() -> dict[str, str]:
    """Return a placeholder payload showing slice registration."""
    return {"message": "Example slice endpoint", "details": "Replace with real slice logic when available."}
