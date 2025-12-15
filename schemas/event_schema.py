from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    FULL = "full"


class EventCategory(str, Enum):
    ESPORTES = "Esportes"
    MUSICA = "Música"
    TECNOLOGIA = "Tecnologia"
    ARTE = "Arte"
    EDUCACAO = "Educação"
    GASTRONOMIA = "Gastronomia"
    NETWORKING = "Networking"
    OUTROS = "Outros"


class OrganizerInfo(BaseModel):
    id: str
    name: str
    rating: float = Field(ge=0, le=5)


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    banner: str
    date: str  # ISO 8601 format
    time: str
    price: Optional[float] = None
    capacity: int = Field(gt=0)
    category: str
    description: str
    location: str
    rules: List[str] = []


class EventCreate(EventBase):
    organizer_name: str
    organizer_rating: float = Field(ge=0, le=5, default=5.0)


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    banner: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    price: Optional[float] = None
    capacity: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    rules: Optional[List[str]] = None


class EventStatusUpdate(BaseModel):
    status: EventStatus


class Event(BaseModel):
    id: str
    title: str
    banner: str
    date: str
    price: Optional[float]
    remaining_seats: int
    organizer: OrganizerInfo
    category: str


class ParticipantInfo(BaseModel):
    id: str
    name: str
    city: str
    is_friend: bool = Field(default=False, alias="isFriend")
    
    class Config:
        populate_by_name = True


class EventDetail(BaseModel):
    id: str
    title: str
    banner: str
    date: str
    time: str
    price: Optional[float]
    remaining_seats: int
    capacity: int
    organizer: OrganizerInfo
    category: str
    description: str
    location: str
    rules: List[str]
    status: EventStatus
    participants: List[ParticipantInfo] = []


class EventInDB(EventBase):
    id: str
    organizer_id: str
    organizer_name: str
    organizer_rating: float
    capacity: int
    registered_users: List[str] = []
    status: EventStatus
    created_at: datetime
