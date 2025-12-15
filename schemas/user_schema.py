from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    city: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    id: str
    name: str
    email: str
    city: str
    hashed_password: str
    created_at: datetime
    friends: list[str] = []
    friend_requests_sent: list[str] = []
    friend_requests_received: list[str] = []


class UserPublic(BaseModel):
    id: str
    name: str
    city: str
    is_friend: bool = False


class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    city: str


class Token(BaseModel):
    token: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
