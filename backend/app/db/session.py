from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from typing import AsyncGenerator

# Motor do banco de dados assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Altere para True para debug de SQL
)

# Fábrica de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# Dependency injection para o FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
