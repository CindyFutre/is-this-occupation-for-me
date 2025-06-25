from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Create database connection"""
    global client
    client = AsyncIOMotorClient(settings.database_url)


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()