from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from schemas.registration_schema import RegistrationStatus
from utils.exceptions import (
    RegistrationNotFoundException,
    ForbiddenException,
    CannotCancelException,
    EventNotFoundException
)
from utils.debug import debug_print


class RegistrationService:
    def __init__(
        self,
        user_repo: UserRepository,
        event_repo: EventRepository,
        registration_repo: RegistrationRepository
    ):
        self.user_repo = user_repo
        self.event_repo = event_repo
        self.registration_repo = registration_repo
    
    async def cancel_registration(self, registration_id: str, user_id: str) -> dict:
        """Cancel a registration"""
        debug_print("registration_service.py", "cancel_registration", "variables", registration_id=registration_id, user_id=user_id)
        
        # Get registration
        registration = await self.registration_repo.get_registration_by_id(registration_id)
        if not registration:
            debug_print("registration_service.py", "cancel_registration", "error", error="RegistrationNotFoundException", reason=f"Registration with id {registration_id} not found")
            raise RegistrationNotFoundException()
        
        # Check if user owns this registration
        if registration["usuario_id"] != user_id:
            debug_print("registration_service.py", "cancel_registration", "error", error="ForbiddenException", reason=f"User {user_id} does not own registration {registration_id} (owner: {registration['usuario_id']})")
            raise ForbiddenException()
        
        # Check if registration can be cancelled
        if registration["status"] not in [RegistrationStatus.AGUARDANDO_PAGAMENTO, RegistrationStatus.APROVADA]:
            debug_print("registration_service.py", "cancel_registration", "error", error="CannotCancelException", reason=f"Registration {registration_id} has status {registration['status']}, cannot be cancelled")
            raise CannotCancelException()
        
        # Cancel registration
        await self.registration_repo.cancel_registration(registration_id)
        
        # Remove user from event participants
        await self.event_repo.remove_participant(registration["evento_id"], user_id)
        
        result = {"message": "Registration cancelled successfully"}
        debug_print("registration_service.py", "cancel_registration", "returning", result=result)
        return result
    
    async def update_registration_status(self, registration_id: str, new_status: RegistrationStatus, user_id: str) -> dict:
        """Update registration status (only event organizer can update)"""
        debug_print("registration_service.py", "update_registration_status", "variables", registration_id=registration_id, new_status=new_status, user_id=user_id)
        
        # Get registration
        registration = await self.registration_repo.get_registration_by_id(registration_id)
        if not registration:
            debug_print("registration_service.py", "update_registration_status", "error", error="RegistrationNotFoundException", reason=f"Registration with id {registration_id} not found")
            raise RegistrationNotFoundException()
        
        # Get event to check if user is organizer
        event = await self.event_repo.get_event_by_id(registration["evento_id"])
        if not event:
            debug_print("registration_service.py", "update_registration_status", "error", error="EventNotFoundException", reason=f"Event with id {registration['evento_id']} not found")
            raise EventNotFoundException()
        
        # Only organizer can update registration status
        if event["organizer_id"] != user_id:
            debug_print("registration_service.py", "update_registration_status", "error", error="ForbiddenException", reason=f"User {user_id} is not the organizer of event {event['_id']} (organizer: {event['organizer_id']})")
            raise ForbiddenException()
        
        # Update registration status
        await self.registration_repo.update_registration_status(registration_id, new_status)
        
        # If status is APROVADA and it's a paid event, update payment timestamp
        if new_status == RegistrationStatus.APROVADA and event.get("price", 0) > 0:
            await self.registration_repo.update_payment_timestamp(registration_id)
        
        result = {"message": f"Registration status updated to {new_status} successfully"}
        debug_print("registration_service.py", "update_registration_status", "returning", result=result)
        return result
    
    async def get_event_registrations(self, event_id: str, user_id: str):
        """Get all registrations for an event (only organizer can access)"""
        debug_print("registration_service.py", "get_event_registrations", "variables", event_id=event_id, user_id=user_id)
        
        # Get event to check if user is organizer
        event = await self.event_repo.get_event_by_id(event_id)
        if not event:
            debug_print("registration_service.py", "get_event_registrations", "error", error="EventNotFoundException", reason=f"Event with id {event_id} not found")
            raise EventNotFoundException()
        
        # Only organizer can access registrations
        if event["organizer_id"] != user_id:
            debug_print("registration_service.py", "get_event_registrations", "error", error="ForbiddenException", reason=f"User {user_id} is not the organizer of event {event_id}")
            raise ForbiddenException()
        
        # Get registrations
        registrations = await self.registration_repo.get_event_registrations(event_id)
        
        # Get user details for each registration
        result = []
        for reg in registrations:
            user = await self.user_repo.get_user_by_id(reg["usuario_id"])
            if user:
                registration_with_user = {
                    "id": reg["id"],
                    "eventoId": reg["evento_id"],
                    "usuarioId": reg["usuario_id"],
                    "userName": user["name"],
                    "userEmail": user["email"],
                    "userCity": user["city"],
                    "status": reg["status"],
                    "timestampInscricao": reg["timestamp_inscricao"],
                    "timestampPagamento": reg.get("timestamp_pagamento")
                }
                result.append(registration_with_user)
        
        debug_print("registration_service.py", "get_event_registrations", "returning", registrations_count=len(result))
        return result
    
    async def get_organizer_registrations(self, organizer_id: str):
        """Get all registrations for events organized by user"""
        debug_print("registration_service.py", "get_organizer_registrations", "variables", organizer_id=organizer_id)
        
        # Get all events organized by user
        events = await self.event_repo.get_events_by_organizer(organizer_id)
        
        # Get all registrations for those events
        result = []
        for event in events:
            registrations = await self.registration_repo.get_event_registrations(event["id"])
            
            for reg in registrations:
                user = await self.user_repo.get_user_by_id(reg["usuario_id"])
                if user:
                    registration_with_user = {
                        "id": reg["id"],
                        "eventoId": reg["evento_id"],
                        "usuarioId": reg["usuario_id"],
                        "userName": user["name"],
                        "userEmail": user["email"],
                        "userCity": user["city"],
                        "status": reg["status"],
                        "timestampInscricao": reg["timestamp_inscricao"],
                        "timestampPagamento": reg.get("timestamp_pagamento")
                    }
                    result.append(registration_with_user)
        
        debug_print("registration_service.py", "get_organizer_registrations", "returning", registrations_count=len(result))
        return result
