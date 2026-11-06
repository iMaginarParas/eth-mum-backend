from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import sys

# Validate and fix DATABASE_URL format
def get_database_url() -> str:
    db_url = settings.DATABASE_URL

    # Check if DATABASE_URL exists
    if not db_url:
        error_msg = """
╔════════════════════════════════════════════════════════════════╗
║  ERROR: DATABASE_URL is not set!                              ║
╚════════════════════════════════════════════════════════════════╝

DATABASE_URL is required. Get it from Supabase Dashboard:

1. Go to https://supabase.com/dashboard
2. Select your project
3. Settings → Database
4. Connection String → URI (Connection Pooling) ← IMPORTANT!
5. Copy the URL and replace [YOUR-PASSWORD] with your database password

Example format:
postgresql://postgres.xxxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
        """
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    # Check if it's the wrong format (HTTPS instead of PostgreSQL)
    if db_url.startswith("https://") or db_url.startswith("http://"):
        error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║  ERROR: DATABASE_URL has wrong format!                        ║
╚════════════════════════════════════════════════════════════════╝

Current value: {db_url}

This is the Supabase REST API URL, NOT the database connection string!

Get the PostgreSQL URL from Supabase Dashboard:
Settings → Database → Connection String → Connection Pooling tab

Correct format:
postgresql://postgres.xxxxx:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres

NOT:
https://xxxxx.supabase.co
        """
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    # Check if it starts with postgresql://
    if not db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        error_msg = f"""
╔════════════════════════════════════════════════════════════════╗
║  ERROR: DATABASE_URL must start with "postgresql://"          ║
╚════════════════════════════════════════════════════════════════╝

Current value: {db_url}

Expected format:
postgresql://postgres.xxxxx:password@host:6543/postgres
        """
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    # IMPORTANT: Always use asyncpg driver for async SQLAlchemy
    # Replace postgresql:// with postgresql+asyncpg:// if not already present
    if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return db_url

# Get and validate DATABASE_URL at module import time
database_url = get_database_url()

# Create async engine with asyncpg
engine = create_async_engine(
    database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
