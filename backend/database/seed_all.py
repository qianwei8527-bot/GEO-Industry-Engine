"""Seed all data for fresh database initialization."""
import asyncio
import sys
sys.path.insert(0, '.')
from app.database import _get_session_factory

async def seed_all():
    factory = _get_session_factory()
    async with factory() as db:
        # Try to run provider seed
        try:
            from database.seed_providers import seed_providers
            await seed_providers(db)
            print("seed_providers: OK")
        except Exception as e:
            print("seed_providers skipped: " + str(e))
    print("Seed complete")

if __name__ == "__main__":
    asyncio.run(seed_all())
