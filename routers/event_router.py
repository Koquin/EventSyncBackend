from fastapi import APIRouter, Depends, status
from typing import List
from config.database import get_database
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from repositories.friendship_repository import FriendshipRepository
from services.event_service import EventService
from schemas.event_schema import Event, EventDetail, EventCreate, EventUpdate, EventStatusUpdate
from schemas.registration_schema import RegistrationResponse
from schemas.common_schema import MessageResponse
from middlewares.auth_middleware import get_current_user_id, get_current_user_optional

router = APIRouter(prefix="/events", tags=["Events"])


def get_event_service(db=Depends(get_database)) -> EventService:
    """Dependency to get EventService instance"""
    user_repo = UserRepository(db)
    event_repo = EventRepository(db)
    registration_repo = RegistrationRepository(db)
    friendship_repo = FriendshipRepository(db)
    return EventService(user_repo, event_repo, registration_repo, friendship_repo)


@router.get("", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_all_events(
    event_service: EventService = Depends(get_event_service)
):
    """
    Get all events
    
    Returns a list of all available events with basic information
    """
    return await event_service.get_all_events()


@router.get("/userEvents", response_model=List[RegistrationResponse], status_code=status.HTTP_200_OK)
async def get_user_events(
    current_user_id: str = Depends(get_current_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """
    Get user's event registrations (requires authentication)
    
    Returns a list of all events the user is registered for
    """
    return await event_service.get_user_events(current_user_id)


@router.get("/organizedEvents", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_organized_events(
    current_user_id: str = Depends(get_current_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """
    Get events organized by the logged-in user (requires authentication)
    
    Returns a list of all events where the user is the organizer
    """
    return await event_service.get_organized_events(current_user_id)


@router.get("/{event_id}", response_model=EventDetail, status_code=status.HTTP_200_OK)
async def get_event_detail(
    event_id: str,
    current_user_id: str = Depends(get_current_user_optional),
    event_service: EventService = Depends(get_event_service)
):
    """
    Get detailed information about a specific event
    
    - **event_id**: The ID of the event
    
    Returns complete event details including participants
    """
    response = await event_service.get_event_detail(event_id, current_user_id)
    print("Returning response from get_event_detail:", response)
    return response


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user_id: str = Depends(get_current_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """
    Create a new event (requires authentication)
    
    The logged-in user will be set as the organizer
    """
    event_dict = event_data.model_dump()
    result = await event_service.create_event(event_dict, current_user_id)
    return MessageResponse(message=result["message"])


@router.put("/{event_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user_id: str = Depends(get_current_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """
    Update an event (requires authentication and ownership)
    
    - **event_id**: The ID of the event to update
    
    Only the organizer can update the event
    """
    update_dict = event_data.model_dump(exclude_none=True)
    result = await event_service.update_event(event_id, update_dict, current_user_id)
    return MessageResponse(message=result["message"])


@router.patch("/{event_id}/status", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def update_event_status(
    event_id: str,
    status_data: EventStatusUpdate,
    current_user_id: str = Depends(get_current_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """
    Update event status (requires authentication and ownership)
    
    - **event_id**: The ID of the event
    - **status**: New status (open, closed, or full)
    
    Only the organizer can update the event status
    """
    result = await event_service.update_event_status(event_id, status_data.status, current_user_id)
    return MessageResponse(message=result["message"])


@router.post("/{event_id}/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_for_event(
    event_id: str,
    current_user_id: str = Depends(get_current_user_id),
    event_service: EventService = Depends(get_event_service)
):
    """
    Register for an event (requires authentication)
    
    - **event_id**: The ID of the event to register for
    
    Returns confirmation of registration
    """
    result = await event_service.register_for_event(event_id, current_user_id)
    return MessageResponse(message=result["message"])
