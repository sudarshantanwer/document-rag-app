from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import Base
from app.db.session import DATABASE_URL
import asyncio

async def create_tables():
    """Create all database tables"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
