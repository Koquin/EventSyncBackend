from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from utils.debug import debug_print


class FriendshipRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["friendships"]
    
    async def create_friendship_request(self, from_user_id: str, to_user_id: str) -> str:
        """Create a new friendship request"""
        debug_print("friendship_repository.py", "create_friendship_request", "variables", from_user_id=from_user_id, to_user_id=to_user_id)
        
        friendship_data = {
            "solicitante_id": from_user_id,
            "destinatario_id": to_user_id,
            "status": "pending",
            "timestamp": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(friendship_data)
        friendship_id = str(result.inserted_id)
        
        debug_print("friendship_repository.py", "create_friendship_request", "returning", friendship_id=friendship_id)
        return friendship_id
    
    async def get_friendship_by_users(self, user1_id: str, user2_id: str) -> Optional[dict]:
        """Get friendship between two users (in any direction)"""
        debug_print("friendship_repository.py", "get_friendship_by_users", "variables", user1_id=user1_id, user2_id=user2_id)
        
        friendship = await self.collection.find_one({
            "$or": [
                {"solicitante_id": user1_id, "destinatario_id": user2_id},
                {"solicitante_id": user2_id, "destinatario_id": user1_id}
            ]
        })
        
        if friendship:
            friendship["id"] = str(friendship["_id"])
        
        debug_print("friendship_repository.py", "get_friendship_by_users", "returning", friendship=friendship)
        return friendship
    
    async def accept_friendship_request(self, friendship_id: str) -> bool:
        """Accept a friendship request"""
        debug_print("friendship_repository.py", "accept_friendship_request", "variables", friendship_id=friendship_id)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(friendship_id)},
                {"$set": {"status": "accepted"}}
            )
            success = result.modified_count > 0
            debug_print("friendship_repository.py", "accept_friendship_request", "returning", success=success)
            return success
        except:
            debug_print("friendship_repository.py", "accept_friendship_request", "returning", success=False)
            return False
    
    async def check_friendship(self, user1_id: str, user2_id: str) -> bool:
        """Check if two users are friends (accepted status)"""
        debug_print("friendship_repository.py", "check_friendship", "variables", user1_id=user1_id, user2_id=user2_id)
        
        friendship = await self.collection.find_one({
            "$or": [
                {"solicitante_id": user1_id, "destinatario_id": user2_id, "status": "accepted"},
                {"solicitante_id": user2_id, "destinatario_id": user1_id, "status": "accepted"}
            ]
        })
        
        result = friendship is not None
        debug_print("friendship_repository.py", "check_friendship", "returning", result=result)
        return result
    
    async def get_pending_requests_received(self, user_id: str) -> List[dict]:
        """Get all pending friendship requests received by a user"""
        debug_print("friendship_repository.py", "get_pending_requests_received", "variables", user_id=user_id)
        
        cursor = self.collection.find({
            "destinatario_id": user_id,
            "status": "pending"
        })
        
        requests = []
        async for request in cursor:
            request["id"] = str(request["_id"])
            requests.append(request)
        
        debug_print("friendship_repository.py", "get_pending_requests_received", "returning", requests_count=len(requests))
        return requests
    
    async def get_all_friends(self, user_id: str) -> List[str]:
        """Get all friend IDs for a user (accepted friendships)"""
        debug_print("friendship_repository.py", "get_all_friends", "variables", user_id=user_id)
        
        cursor = self.collection.find({
            "$or": [
                {"solicitante_id": user_id, "status": "accepted"},
                {"destinatario_id": user_id, "status": "accepted"}
            ]
        })
        
        friend_ids = []
        async for friendship in cursor:
            # Get the other user's ID
            if friendship["solicitante_id"] == user_id:
                friend_ids.append(friendship["destinatario_id"])
            else:
                friend_ids.append(friendship["solicitante_id"])
        
        debug_print("friendship_repository.py", "get_all_friends", "returning", friend_ids=friend_ids)
        return friend_ids
