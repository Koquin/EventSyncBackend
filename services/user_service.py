from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from repositories.friendship_repository import FriendshipRepository
from utils.exceptions import UserNotFoundException
from utils.debug import debug_print


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        event_repo: EventRepository,
        registration_repo: RegistrationRepository,
        friendship_repo: FriendshipRepository
    ):
        self.user_repo = user_repo
        self.event_repo = event_repo
        self.registration_repo = registration_repo
        self.friendship_repo = friendship_repo
    
    async def send_friend_request(self, from_user_id: str, to_user_id: str) -> dict:
        """Send a friend request"""
        debug_print("user_service.py", "send_friend_request", "variables", from_user_id=from_user_id, to_user_id=to_user_id)
        
        # Check if target user exists
        target_user = await self.user_repo.get_user_by_id(to_user_id)
        if not target_user:
            debug_print("user_service.py", "send_friend_request", "error", error="UserNotFoundException", reason=f"User with id {to_user_id} not found")
            raise UserNotFoundException()
        
        # Check if friendship already exists (in any status)
        existing_friendship = await self.friendship_repo.get_friendship_by_users(from_user_id, to_user_id)
        if existing_friendship:
            if existing_friendship["status"] == "accepted":
                result = {"message": "You are already friends with this user"}
            else:
                result = {"message": "Friend request already sent"}
            debug_print("user_service.py", "send_friend_request", "returning", result=result)
            return result
        
        # Create friend request
        friendship_id = await self.friendship_repo.create_friendship_request(from_user_id, to_user_id)
        
        if friendship_id:
            result = {"message": "Friend request sent successfully"}
        else:
            result = {"message": "Failed to send friend request"}
        
        debug_print("user_service.py", "send_friend_request", "returning", result=result)
        return result
    
    async def get_user_info(self, user_id: str) -> dict:
        """Get user information by ID"""
        debug_print("user_service.py", "get_user_info", "variables", user_id=user_id)
        
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            debug_print("user_service.py", "get_user_info", "error", error="UserNotFoundException", reason=f"User with id {user_id} not found")
            raise UserNotFoundException()
        
        user_info = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "city": user["city"]
        }
        
        debug_print("user_service.py", "get_user_info", "returning", user_info=user_info)
        return user_info
