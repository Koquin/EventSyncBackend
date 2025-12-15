from fastapi import Depends, Header
from typing import Optional
from utils.auth import decode_access_token
from utils.exceptions import UnauthorizedException
from repositories.user_repository import UserRepository
from config.database import get_database
from utils.debug import debug_print


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Dependency to get current user ID from JWT token"""
    if not authorization:
        debug_print("auth_middleware.py", "get_current_user_id", "error", error="UnauthorizedException", reason="No authorization header provided")
        raise UnauthorizedException()
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            debug_print("auth_middleware.py", "get_current_user_id", "error", error="UnauthorizedException", reason=f"Invalid scheme: {scheme}, expected Bearer")
            raise UnauthorizedException()
    except ValueError:
        debug_print("auth_middleware.py", "get_current_user_id", "error", error="UnauthorizedException", reason="Invalid authorization header format")
        raise UnauthorizedException()
    
    # Decode token
    user_id = decode_access_token(token)
    if not user_id:
        debug_print("auth_middleware.py", "get_current_user_id", "error", error="UnauthorizedException", reason="Invalid or expired token")
        raise UnauthorizedException()
    
    return user_id


async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Dependency to get current user ID from JWT token (optional)"""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    user_id = decode_access_token(token)
    return user_id
