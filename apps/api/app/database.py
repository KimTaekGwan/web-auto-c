from typing import AsyncGenerator
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite 데이터베이스 URL
SQLITE_URL = "sqlite+aiosqlite:///./webcapture.db"

# SQLAlchemy 엔진 생성
engine = create_async_engine(
    SQLITE_URL, echo=True, connect_args={"check_same_thread": False}
)

# 세션 팩토리 생성
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base 클래스 생성
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션을 위한 의존성 주입 함수
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    데이터베이스 초기화 함수
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
