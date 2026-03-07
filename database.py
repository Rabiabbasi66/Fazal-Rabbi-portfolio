from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print(f"Connected to MongoDB at {settings.MONGODB_URL}")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client is not None:
        db.client.close()
        db.client = None
        print("Closed MongoDB connection")


def get_database():
    """Get database instance"""
    if db.client is None:
        raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongo first.")
    return db.client[settings.DATABASE_NAME]


# Collection helpers
def get_collection(collection_name: str):
    """Get a specific collection"""
    database = get_database()
    return database[collection_name]