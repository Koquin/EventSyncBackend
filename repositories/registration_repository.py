from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.registration_schema import RegistrationStatus
from utils.debug import debug_print


class RegistrationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["registrations"]
    
    async def create_registration(self, user_id: str, event_id: str, status: RegistrationStatus = RegistrationStatus.AGUARDANDO_PAGAMENTO) -> str:
        """Create a new registration"""
        debug_print("registration_repository.py", "create_registration", "variables", user_id=user_id, event_id=event_id, status=status)
        
        registration_data = {
            "usuario_id": user_id,
            "evento_id": event_id,
            "status": status,
            "timestamp_inscricao": datetime.utcnow(),
            "timestamp_pagamento": None
        }
        
        result = await self.collection.insert_one(registration_data)
        registration_id = str(result.inserted_id)
        
        debug_print("registration_repository.py", "create_registration", "returning", registration_id=registration_id)
        return registration_id
    
    async def get_registration_by_id(self, registration_id: str) -> Optional[dict]:
        """Get registration by ID"""
        debug_print("registration_repository.py", "get_registration_by_id", "variables", registration_id=registration_id)
        
        try:
            registration = await self.collection.find_one({"_id": ObjectId(registration_id)})
            if registration:
                registration["id"] = str(registration["_id"])
            debug_print("registration_repository.py", "get_registration_by_id", "returning", registration=registration)
            return registration
        except:
            debug_print("registration_repository.py", "get_registration_by_id", "returning", registration=None)
            return None
    
    async def get_user_registrations(self, user_id: str) -> List[dict]:
        """Get all registrations for a user"""
        debug_print("registration_repository.py", "get_user_registrations", "variables", user_id=user_id)
        
        cursor = self.collection.find({"usuario_id": user_id})
        registrations = []
        async for registration in cursor:
            registration["id"] = str(registration["_id"])
            registrations.append(registration)
        
        debug_print("registration_repository.py", "get_user_registrations", "returning", registrations_count=len(registrations))
        return registrations
    
    async def get_registration_by_user_and_event(self, user_id: str, event_id: str) -> Optional[dict]:
        """Check if user is already registered for an event"""
        debug_print("registration_repository.py", "get_registration_by_user_and_event", "variables", user_id=user_id, event_id=event_id)
        
        registration = await self.collection.find_one({
            "usuario_id": user_id,
            "evento_id": event_id,
            "status": {"$nin": [RegistrationStatus.CANCELADA, RegistrationStatus.RECUSADA]}
        })
        if registration:
            registration["id"] = str(registration["_id"])
        
        debug_print("registration_repository.py", "get_registration_by_user_and_event", "returning", registration=registration)
        return registration
    
    async def cancel_registration(self, registration_id: str) -> bool:
        """Cancel a registration"""
        debug_print("registration_repository.py", "cancel_registration", "variables", registration_id=registration_id)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(registration_id)},
                {
                    "$set": {
                        "status": RegistrationStatus.CANCELADA
                    }
                }
            )
            success = result.modified_count > 0
            debug_print("registration_repository.py", "cancel_registration", "returning", success=success)
            return success
        except:
            debug_print("registration_repository.py", "cancel_registration", "returning", success=False)
            return False
    
    async def update_registration_status(self, registration_id: str, status: RegistrationStatus) -> bool:
        """Update registration status"""
        debug_print("registration_repository.py", "update_registration_status", "variables", registration_id=registration_id, status=status)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(registration_id)},
                {"$set": {"status": status}}
            )
            success = result.modified_count > 0
            debug_print("registration_repository.py", "update_registration_status", "returning", success=success)
            return success
        except:
            debug_print("registration_repository.py", "update_registration_status", "returning", success=False)
            return False
    
    async def update_payment_timestamp(self, registration_id: str) -> bool:
        """Update payment timestamp when payment is confirmed"""
        debug_print("registration_repository.py", "update_payment_timestamp", "variables", registration_id=registration_id)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(registration_id)},
                {"$set": {"timestamp_pagamento": datetime.utcnow()}}
            )
            success = result.modified_count > 0
            debug_print("registration_repository.py", "update_payment_timestamp", "returning", success=success)
            return success
        except:
            debug_print("registration_repository.py", "update_payment_timestamp", "returning", success=False)
            return False
    
    async def get_event_registrations(self, event_id: str) -> List[dict]:
        """Get all registrations for an event"""
        debug_print("registration_repository.py", "get_event_registrations", "variables", event_id=event_id)
        
        cursor = self.collection.find({
            "evento_id": event_id,
            "status": {"$nin": [RegistrationStatus.CANCELADA, RegistrationStatus.RECUSADA]}
        })
        registrations = []
        async for registration in cursor:
            registration["id"] = str(registration["_id"])
            registrations.append(registration)
        
        debug_print("registration_repository.py", "get_event_registrations", "returning", registrations_count=len(registrations))
        return registrations
