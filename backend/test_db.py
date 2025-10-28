import asyncio
from core.database import init_db

async def test_db():
    print("Testing database initialization...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(test_db())