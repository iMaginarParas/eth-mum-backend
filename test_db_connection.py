#!/usr/bin/env python3
"""
Test database connection to verify DATABASE_URL is correct
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine


async def test_connection():
    # Prompt for DATABASE_URL
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    print("\nPaste your Supabase DATABASE_URL here:")
    print("(Get it from: Supabase Dashboard → Settings → Database → Connection Pooling)")
    print("\nFormat should be:")
    print("postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres")
    print("\n" + "=" * 60)

    database_url = input("\nDATABASE_URL: ").strip()

    if not database_url:
        print("\n❌ ERROR: DATABASE_URL cannot be empty")
        sys.exit(1)

    # Validate format
    if database_url.startswith("https://") or database_url.startswith("http://"):
        print("\n❌ ERROR: This is the Supabase REST API URL, not the database connection string!")
        print("\nYou need the PostgreSQL connection string from:")
        print("Supabase Dashboard → Settings → Database → Connection String → Connection Pooling")
        sys.exit(1)

    if not database_url.startswith("postgresql://"):
        print("\n❌ ERROR: DATABASE_URL must start with 'postgresql://'")
        sys.exit(1)

    # Convert to asyncpg format
    if not database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"\n🔍 Testing connection to: {database_url.split('@')[0].split(':')[0]}@[HIDDEN]...")

    try:
        # Create engine
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()

        await engine.dispose()

        print("\n✅ SUCCESS! Database connection works!")
        print(f"PostgreSQL version: {version.split(',')[0]}")
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Go to Railway Dashboard: https://railway.app/dashboard")
        print("2. Select your backend project")
        print("3. Click 'Variables' tab")
        print("4. Update DATABASE_URL with the connection string you just tested")
        print("5. Railway will automatically redeploy")
        print("\nYour backend should start successfully after this!")

    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"Error: {e}")
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING:")
        print("=" * 60)
        print("1. Check your database password is correct")
        print("2. Make sure you're using 'Connection Pooling' mode (port 6543)")
        print("3. Verify your Supabase project is active")
        print("4. Check the connection string format matches:")
        print("   postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_connection())
