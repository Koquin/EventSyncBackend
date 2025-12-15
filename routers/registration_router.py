from fastapi import APIRouter, Depends, status
from typing import List
from config.database import get_database
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from services.registration_service import RegistrationService
from schemas.common_schema import MessageResponse
from schemas.registration_schema import RegistrationStatus, RegistrationWithUser
from pydantic import BaseModel
from middlewares.auth_middleware import get_current_user_id
from utils.debug import debug_print

router = APIRouter(prefix="/registrations", tags=["Registrations"])


class RegistrationStatusUpdate(BaseModel):
    status: RegistrationStatus


def get_registration_service(db=Depends(get_database)) -> RegistrationService:
    """Dependency to get RegistrationService instance"""
    user_repo = UserRepository(db)
    event_repo = EventRepository(db)
    registration_repo = RegistrationRepository(db)
    return RegistrationService(user_repo, event_repo, registration_repo)


@router.get("/organizer", response_model=List[RegistrationWithUser], status_code=status.HTTP_200_OK)
async def get_organizer_registrations(
    current_user_id: str = Depends(get_current_user_id),
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Get all registrations for events organized by the logged-in user
    
    Returns list of all registrations for user's organized events
    """
    debug_print("registration_router.py", "get_organizer_registrations", "variables", current_user_id=current_user_id)
    registrations = await registration_service.get_organizer_registrations(current_user_id)
    debug_print("registration_router.py", "get_organizer_registrations", "returning", registrations_count=len(registrations))
    return registrations


@router.get("/event/{event_id}", response_model=List[RegistrationWithUser], status_code=status.HTTP_200_OK)
async def get_event_registrations(
    event_id: str,
    current_user_id: str = Depends(get_current_user_id),
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Get all registrations for an event (only organizer can access)
    
    - **event_id**: The ID of the event
    
    Returns list of registrations with user information
    """
    debug_print("registration_router.py", "get_event_registrations", "variables", event_id=event_id, current_user_id=current_user_id)
    registrations = await registration_service.get_event_registrations(event_id, current_user_id)
    debug_print("registration_router.py", "get_event_registrations", "returning", registrations_count=len(registrations))
    return registrations


@router.post("/{registration_id}/cancel", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def cancel_registration(
    registration_id: str,
    current_user_id: str = Depends(get_current_user_id),
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Cancel a registration (requires authentication)
    
    - **registration_id**: The ID of the registration to cancel
    
    Returns confirmation of cancellation
    """
    result = await registration_service.cancel_registration(registration_id, current_user_id)
    return MessageResponse(message=result["message"])


@router.patch("/{registration_id}/status", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def update_registration_status(
    registration_id: str,
    status_update: RegistrationStatusUpdate,
    current_user_id: str = Depends(get_current_user_id),
    registration_service: RegistrationService = Depends(get_registration_service)
):
    """
    Update registration status (only event organizer can update)
    
    - **registration_id**: The ID of the registration to update
    - **status**: New registration status (aguardando_pagamento, aprovada, recusada, cancelada, finalizada)
    
    Returns confirmation of status update
    """
    result = await registration_service.update_registration_status(registration_id, status_update.status, current_user_id)
    return MessageResponse(message=result["message"])
