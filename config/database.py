from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "eventsync")
        
        cls.client = AsyncIOMotorClient(mongodb_url)
        cls.db = cls.client[db_name]
        print(f"✅ Connected to MongoDB: {db_name}")

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("❌ Closed MongoDB connection")

    @classmethod
    def get_db(cls):
        """Get database instance"""
        return cls.db


# Singleton instance
database = Database()


def get_database():
    """Dependency for FastAPI routes"""
    return database.get_db()
