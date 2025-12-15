from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.user_schema import UserInDB
from utils.debug import debug_print


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]
    
    async def create_user(self, user_data: dict) -> str:
        """Create a new user and return the user ID"""
        debug_print("user_repository.py", "create_user", "variables", user_data=user_data)
        
        user_data["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        debug_print("user_repository.py", "create_user", "returning", user_id=user_id)
        return user_id
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        debug_print("user_repository.py", "get_user_by_email", "variables", email=email)
        
        user = await self.collection.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
        
        debug_print("user_repository.py", "get_user_by_email", "returning", user=user)
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Find user by ID"""
        debug_print("user_repository.py", "get_user_by_id", "variables", user_id=user_id)
        
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
            debug_print("user_repository.py", "get_user_by_id", "returning", user=user)
            return user
        except:
            debug_print("user_repository.py", "get_user_by_id", "returning", user=None)
            return None
    
    async def get_users_by_ids(self, user_ids: List[str]) -> List[dict]:
        """Get multiple users by their IDs"""
        debug_print("user_repository.py", "get_users_by_ids", "variables", user_ids=user_ids)
        
        object_ids = []
        for uid in user_ids:
            try:
                object_ids.append(ObjectId(uid))
            except:
                continue
        
        cursor = self.collection.find({"_id": {"$in": object_ids}})
        users = []
        async for user in cursor:
            user["id"] = str(user["_id"])
            users.append(user)
        
        debug_print("user_repository.py", "get_users_by_ids", "returning", users=users)
        return users
    

