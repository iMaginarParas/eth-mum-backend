"""
Initialize database tables.
Run this script to create all tables in the database.
"""
import asyncio
from app.core.database import engine, Base
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.refund import Refund


async def init_db():
    """Create all tables in the database."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        # Drop all tables first (comment this out in production!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✓ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
