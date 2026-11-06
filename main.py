from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import payments, merchants, invoices, refunds

app = FastAPI(
    title="PayLink API",
    description="USDT Payment Infrastructure for Global Businesses",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(merchants.router)
app.include_router(payments.router)
app.include_router(invoices.router)
app.include_router(refunds.router)


@app.get("/")
async def root():
    return {
        "message": "PayLink API - USDT Payment Infrastructure",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    from app.services.blockchain import blockchain_service

    return {
        "status": "healthy",
        "blockchain_connected": blockchain_service.is_connected(),
        "chain_id": blockchain_service.chain_id
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
