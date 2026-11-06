from fastapi import APIRouter

router = APIRouter(prefix="/api/refunds", tags=["refunds"])

# Placeholder - refunds functionality to be implemented
@router.get("/")
async def list_refunds():
    return {"message": "Refunds API - Coming soon"}
