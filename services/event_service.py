from typing import List
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from repositories.friendship_repository import FriendshipRepository
from schemas.event_schema import Event, EventDetail, OrganizerInfo, ParticipantInfo, EventStatus
from schemas.registration_schema import RegistrationResponse, RegistrationStatus
from utils.exceptions import (
    EventNotFoundException,
    EventFullException,
    AlreadyRegisteredException,
    NotEventOrganizerException
)
from utils.debug import debug_print


class EventService:
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
    
    async def get_all_events(self) -> List[Event]:
        """Get all events"""
        debug_print("event_service.py", "get_all_events", "variables")
        
        events_data = await self.event_repo.get_all_events()
        
        events = []
        for event_data in events_data:
            remaining_seats = event_data["capacity"] - len(event_data.get("registered_users", []))
            
            event = Event(
                id=event_data["id"],
                title=event_data["title"],
                banner=event_data["banner"],
                date=event_data["date"],
                price=event_data.get("price"),
                remaining_seats=remaining_seats,
                organizer=OrganizerInfo(
                    id=event_data["organizer_id"],
                    name=event_data["organizer_name"],
                    rating=event_data["organizer_rating"]
                ),
                category=event_data["category"]
            )
            events.append(event)
        
        debug_print("event_service.py", "get_all_events", "returning", events_count=len(events))
        return events
    
    async def get_organized_events(self, organizer_id: str) -> List[Event]:
        """Get all events organized by a specific user"""
        debug_print("event_service.py", "get_organized_events", "variables", organizer_id=organizer_id)
        
        events_data = await self.event_repo.get_events_by_organizer(organizer_id)
        
        events = []
        for event_data in events_data:
            remaining_seats = event_data["capacity"] - len(event_data.get("registered_users", []))
            
            event = Event(
                id=event_data["id"],
                title=event_data["title"],
                banner=event_data["banner"],
                date=event_data["date"],
                price=event_data.get("price"),
                remaining_seats=remaining_seats,
                organizer=OrganizerInfo(
                    id=event_data["organizer_id"],
                    name=event_data["organizer_name"],
                    rating=event_data["organizer_rating"]
                ),
                category=event_data["category"]
            )
            events.append(event)
        
        debug_print("event_service.py", "get_organized_events", "returning", events_count=len(events))
        return events
    
    async def get_event_detail(self, event_id: str, current_user_id: str = None) -> EventDetail:
        """Get event details"""
        debug_print("event_service.py", "get_event_detail", "variables", event_id=event_id, current_user_id=current_user_id)
        
        event_data = await self.event_repo.get_event_by_id(event_id)
        if not event_data:
            debug_print("event_service.py", "get_event_detail", "error", error="EventNotFoundException", reason=f"Event with id {event_id} not found")
            raise EventNotFoundException()
        
        # Get participants info
        participants = []
        registered_user_ids = event_data.get("registered_users", [])
        
        if registered_user_ids:
            users = await self.user_repo.get_users_by_ids(registered_user_ids)
            
            for user in users:
                is_friend = False
                if current_user_id:
                    is_friend = await self.friendship_repo.check_friendship(current_user_id, user["id"])
                
                participant = ParticipantInfo(
                    id=user["id"],
                    name=user["name"],
                    city=user["city"],
                    isFriend=is_friend
                )
                participants.append(participant)
        
        remaining_seats = event_data["capacity"] - len(registered_user_ids)
        
        event_detail = EventDetail(
            id=event_data["id"],
            title=event_data["title"],
            banner=event_data["banner"],
            date=event_data["date"],
            time=event_data["time"],
            price=event_data.get("price"),
            remaining_seats=remaining_seats,
            capacity=event_data["capacity"],
            organizer=OrganizerInfo(
                id=event_data["organizer_id"],
                name=event_data["organizer_name"],
                rating=event_data["organizer_rating"]
            ),
            category=event_data["category"],
            description=event_data["description"],
            location=event_data["location"],
            rules=event_data.get("rules", []),
            status=event_data["status"],
            participants=participants
        )
        
        debug_print("event_service.py", "get_event_detail", "returning", event_id=event_detail.id, participants_count=len(participants))
        return event_detail
    
    async def get_user_events(self, user_id: str) -> List[RegistrationResponse]:
        """Get user's event registrations"""
        debug_print("event_service.py", "get_user_events", "variables", user_id=user_id)
        
        registrations = await self.registration_repo.get_user_registrations(user_id)
        
        if not registrations:
            debug_print("event_service.py", "get_user_events", "returning", result=[])
            return []
        
        # Get event IDs
        event_ids = [reg["evento_id"] for reg in registrations]
        events = await self.event_repo.get_events_by_ids(event_ids)
        
        # Create a map of event_id -> event
        event_map = {event["id"]: event for event in events}
        
        result = []
        for reg in registrations:
            event = event_map.get(reg["evento_id"])
            if not event:
                continue
            
            # Can cancel if status is aguardando_pagamento or aprovada
            can_cancel = reg["status"] in [RegistrationStatus.AGUARDANDO_PAGAMENTO, RegistrationStatus.APROVADA]
            
            response = RegistrationResponse(
                id=reg["id"],
                eventId=reg["evento_id"],
                eventName=event["title"],
                eventDate=event["date"],
                eventBanner=event["banner"],
                status=reg["status"],
                timestampInscricao=reg["timestamp_inscricao"],
                timestampPagamento=reg.get("timestamp_pagamento"),
                canCancel=can_cancel
            )
            result.append(response)
        
        debug_print("event_service.py", "get_user_events", "returning", registrations_count=len(result))
        return result
    
    async def register_for_event(self, event_id: str, user_id: str) -> dict:
        """Register user for an event"""
        debug_print("event_service.py", "register_for_event", "variables", event_id=event_id, user_id=user_id)
        
        # Check if event exists
        event = await self.event_repo.get_event_by_id(event_id)
        if not event:
            debug_print("event_service.py", "register_for_event", "error", error="EventNotFoundException", reason=f"Event with id {event_id} not found")
            raise EventNotFoundException()
        
        # Check if event is full
        if event["status"] == EventStatus.FULL:
            debug_print("event_service.py", "register_for_event", "error", error="EventFullException", reason=f"Event {event_id} has status FULL")
            raise EventFullException()
        
        remaining_seats = event["capacity"] - len(event.get("registered_users", []))
        if remaining_seats <= 0:
            debug_print("event_service.py", "register_for_event", "error", error="EventFullException", reason=f"Event {event_id} has no remaining seats (capacity: {event['capacity']}, registered: {len(event.get('registered_users', []))})")
            raise EventFullException()
        
        # Check if user is already registered
        existing_registration = await self.registration_repo.get_registration_by_user_and_event(
            user_id, event_id
        )
        if existing_registration:
            debug_print("event_service.py", "register_for_event", "error", error="AlreadyRegisteredException", reason=f"User {user_id} is already registered for event {event_id}")
            raise AlreadyRegisteredException()
        
        # Determine initial status based on event price
        if event.get("price") is None or event.get("price") == 0:
            initial_status = RegistrationStatus.APROVADA
        else:
            initial_status = RegistrationStatus.AGUARDANDO_PAGAMENTO
        
        # Create registration with determined status
        registration_id = await self.registration_repo.create_registration(user_id, event_id, initial_status)
        
        # Add user to event participants
        await self.event_repo.add_participant(event_id, user_id)
        
        # Update payment timestamp if free event
        if initial_status == RegistrationStatus.APROVADA:
            await self.registration_repo.update_payment_timestamp(registration_id)
        
        result = {
            "message": "Registration successful",
            "registration_id": registration_id
        }
        debug_print("event_service.py", "register_for_event", "returning", result=result)
        return result
    
    async def create_event(self, event_data: dict, organizer_id: str) -> dict:
        """Create a new event"""
        debug_print("event_service.py", "create_event", "variables", event_data=event_data, organizer_id=organizer_id)
        
        # Add organizer_id to event data
        event_data["organizer_id"] = organizer_id
        
        # Create event
        event_id = await self.event_repo.create_event(event_data)
        
        result = {
            "message": "Event created successfully",
            "event_id": event_id
        }
        debug_print("event_service.py", "create_event", "returning", result=result)
        return result
    
    async def update_event(self, event_id: str, update_data: dict, user_id: str) -> dict:
        """Update an event"""
        debug_print("event_service.py", "update_event", "variables", event_id=event_id, update_data=update_data, user_id=user_id)
        
        # Check if event exists
        event = await self.event_repo.get_event_by_id(event_id)
        if not event:
            debug_print("event_service.py", "update_event", "error", error="EventNotFoundException", reason=f"Event with id {event_id} not found")
            raise EventNotFoundException()
        
        # Check if user is the organizer
        if event["organizer_id"] != user_id:
            debug_print("event_service.py", "update_event", "error", error="NotEventOrganizerException", reason=f"User {user_id} is not the organizer of event {event_id}")
            raise NotEventOrganizerException()
        
        # If price is 0, empty string, or None, set to None (free event)
        if "price" in update_data and (update_data["price"] == 0 or update_data["price"] == "" or update_data["price"] is None):
            update_data["price"] = None
        
        # Update event
        success = await self.event_repo.update_event(event_id, update_data)
        
        if success:
            result = {"message": "Event updated successfully"}
        else:
            result = {"message": "No changes were made"}
        
        debug_print("event_service.py", "update_event", "returning", result=result)
        return result
    
    async def update_event_status(self, event_id: str, new_status: str, user_id: str) -> dict:
        """Update event status"""
        debug_print("event_service.py", "update_event_status", "variables", event_id=event_id, new_status=new_status, user_id=user_id)
        
        # Check if event exists
        event = await self.event_repo.get_event_by_id(event_id)
        if not event:
            debug_print("event_service.py", "update_event_status", "error", error="EventNotFoundException", reason=f"Event with id {event_id} not found")
            raise EventNotFoundException()
        
        # Check if user is the organizer
        if event["organizer_id"] != user_id:
            debug_print("event_service.py", "update_event_status", "error", error="NotEventOrganizerException", reason=f"User {user_id} is not the organizer of event {event_id}")
            raise NotEventOrganizerException()
        
        # Update status
        success = await self.event_repo.update_event_status(event_id, new_status)
        
        result = {"message": f"Event status updated to {new_status}"}
        debug_print("event_service.py", "update_event_status", "returning", result=result)
        return result
