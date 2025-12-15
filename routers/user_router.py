from fastapi import APIRouter, Depends, status
from config.database import get_database
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from repositories.friendship_repository import FriendshipRepository
from services.user_service import UserService
from schemas.common_schema import MessageResponse
from schemas.user_schema import UserInfo
from middlewares.auth_middleware import get_current_user_id
from utils.debug import debug_print

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db=Depends(get_database)) -> UserService:
    """Dependency to get UserService instance"""
    user_repo = UserRepository(db)
    event_repo = EventRepository(db)
    registration_repo = RegistrationRepository(db)
    friendship_repo = FriendshipRepository(db)
    return UserService(user_repo, event_repo, registration_repo, friendship_repo)


@router.get("/me", response_model=UserInfo, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current user information from token (requires authentication)
    
    Returns user information (id, name, email, city)
    """
    debug_print("user_router.py", "get_current_user_info", "variables", current_user_id=current_user_id)
    user_info = await user_service.get_user_info(current_user_id)
    debug_print("user_router.py", "get_current_user_info", "returning", user_info=user_info)
    return UserInfo(**user_info)


@router.post("/{user_id}/friend-request", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Send a friend request to another user (requires authentication)
    
    - **user_id**: The ID of the user to send the friend request to
    
    Returns confirmation of request sent
    """
    result = await user_service.send_friend_request(current_user_id, user_id)
    return MessageResponse(message=result["message"])
