from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.event_schema import EventStatus
from utils.debug import debug_print


class EventRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["events"]
    
    async def create_event(self, event_data: dict) -> str:
        """Create a new event and return the event ID"""
        debug_print("event_repository.py", "create_event", "variables", event_data=event_data)
        
        event_data["created_at"] = datetime.utcnow()
        event_data["registered_users"] = []
        event_data["status"] = EventStatus.OPEN
        
        result = await self.collection.insert_one(event_data)
        event_id = str(result.inserted_id)
        
        debug_print("event_repository.py", "create_event", "returning", event_id=event_id)
        return event_id
    
    async def get_all_events(self) -> List[dict]:
        """Get all events"""
        debug_print("event_repository.py", "get_all_events", "variables")
        
        cursor = self.collection.find({})
        events = []
        async for event in cursor:
            event["id"] = str(event["_id"])
            events.append(event)
        
        debug_print("event_repository.py", "get_all_events", "returning", events_count=len(events))
        return events
    
    async def get_event_by_id(self, event_id: str) -> Optional[dict]:
        """Get event by ID"""
        debug_print("event_repository.py", "get_event_by_id", "variables", event_id=event_id)
        
        try:
            event = await self.collection.find_one({"_id": ObjectId(event_id)})
            if event:
                event["id"] = str(event["_id"])
            debug_print("event_repository.py", "get_event_by_id", "returning", event=event)
            return event
        except:
            debug_print("event_repository.py", "get_event_by_id", "returning", event=None)
            return None
    
    async def get_events_by_ids(self, event_ids: List[str]) -> List[dict]:
        """Get multiple events by their IDs"""
        debug_print("event_repository.py", "get_events_by_ids", "variables", event_ids=event_ids)
        
        object_ids = []
        for eid in event_ids:
            try:
                object_ids.append(ObjectId(eid))
            except:
                continue
        
        cursor = self.collection.find({"_id": {"$in": object_ids}})
        events = []
        async for event in cursor:
            event["id"] = str(event["_id"])
            events.append(event)
        
        debug_print("event_repository.py", "get_events_by_ids", "returning", events_count=len(events))
        return events
    
    async def get_events_by_organizer(self, organizer_id: str) -> List[dict]:
        """Get all events organized by a specific user"""
        debug_print("event_repository.py", "get_events_by_organizer", "variables", organizer_id=organizer_id)
        
        cursor = self.collection.find({"organizer_id": organizer_id})
        events = []
        async for event in cursor:
            event["id"] = str(event["_id"])
            events.append(event)
        
        debug_print("event_repository.py", "get_events_by_organizer", "returning", events_count=len(events))
        return events
    
    async def add_participant(self, event_id: str, user_id: str) -> bool:
        """Add a participant to an event"""
        debug_print("event_repository.py", "add_participant", "variables", event_id=event_id, user_id=user_id)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$addToSet": {"registered_users": user_id}}
            )
            
            # Update status if event is full
            event = await self.get_event_by_id(event_id)
            if event:
                remaining = event["capacity"] - len(event.get("registered_users", []))
                if remaining <= 0:
                    await self.update_event_status(event_id, EventStatus.FULL)
            
            success = result.modified_count > 0
            debug_print("event_repository.py", "add_participant", "returning", success=success)
            return success
        except:
            debug_print("event_repository.py", "add_participant", "returning", success=False)
            return False
    
    async def remove_participant(self, event_id: str, user_id: str) -> bool:
        """Remove a participant from an event"""
        debug_print("event_repository.py", "remove_participant", "variables", event_id=event_id, user_id=user_id)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$pull": {"registered_users": user_id}}
            )
            
            # Update status if event is no longer full
            event = await self.get_event_by_id(event_id)
            if event and event["status"] == EventStatus.FULL:
                await self.update_event_status(event_id, EventStatus.OPEN)
            
            success = result.modified_count > 0
            debug_print("event_repository.py", "remove_participant", "returning", success=success)
            return success
        except:
            debug_print("event_repository.py", "remove_participant", "returning", success=False)
            return False
    
    async def update_event_status(self, event_id: str, status: EventStatus) -> bool:
        """Update event status"""
        debug_print("event_repository.py", "update_event_status", "variables", event_id=event_id, status=status)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": {"status": status}}
            )
            success = result.modified_count > 0
            debug_print("event_repository.py", "update_event_status", "returning", success=success)
            return success
        except:
            debug_print("event_repository.py", "update_event_status", "returning", success=False)
            return False
    
    async def get_remaining_seats(self, event_id: str) -> int:
        """Get remaining seats for an event"""
        debug_print("event_repository.py", "get_remaining_seats", "variables", event_id=event_id)
        
        event = await self.get_event_by_id(event_id)
        if event:
            remaining = event["capacity"] - len(event.get("registered_users", []))
            debug_print("event_repository.py", "get_remaining_seats", "returning", remaining=remaining)
            return remaining
        
        debug_print("event_repository.py", "get_remaining_seats", "returning", remaining=0)
        return 0
    
    async def update_event(self, event_id: str, update_data: dict) -> bool:
        """Update event fields"""
        debug_print("event_repository.py", "update_event", "variables", event_id=event_id, update_data=update_data)
        
        try:
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_data:
                debug_print("event_repository.py", "update_event", "returning", success=False, reason="No data to update")
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": update_data}
            )
            success = result.modified_count > 0
            debug_print("event_repository.py", "update_event", "returning", success=success)
            return success
        except:
            debug_print("event_repository.py", "update_event", "returning", success=False)
            return False
