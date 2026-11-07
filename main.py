from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import payments, merchants, invoices, refunds, checkout
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Supabase connection
    print("Starting up: Connecting to Supabase...")
    from app.core.supabase import supabase

    # Test connection
    try:
        # Simple ping to verify Supabase is accessible
        supabase.table('merchants').select('id').limit(1).execute()
        print("✓ Supabase connection ready!")
    except Exception as e:
        print(f"⚠ Supabase connection test: {e}")
        print("Note: Tables will be created automatically when first used")

    yield
    # Shutdown: Clean up resources
    print("Shutting down...")


app = FastAPI(
    title="Pocket Pay API",
    description="USDT Payment Infrastructure for Global Businesses",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(merchants.router)
app.include_router(payments.router)
app.include_router(invoices.router)
app.include_router(refunds.router)
app.include_router(checkout.router)


@app.get("/")
async def root():
    return {
        "message": "Pocket Pay API - USDT Payment Infrastructure",
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
