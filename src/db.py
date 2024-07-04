from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# The url of a DB
ASYNC_DB_URL = "postgresql+asyncpg://postgres:postgres@db/pqvector_db"


# Create a engine to the DB
async_engine = create_async_engine(ASYNC_DB_URL)
async_session = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


# Session for the access to the DB
async def get_db():
    async with async_session() as session:
        yield session
