from fastapi import APIRouter

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

# Placeholder - invoices functionality to be implemented
@router.get("/")
async def list_invoices():
    return {"message": "Invoices API - Coming soon"}
