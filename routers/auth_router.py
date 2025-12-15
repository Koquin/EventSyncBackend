from fastapi import APIRouter, Depends, status
from config.database import get_database
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from services.auth_service import AuthService
from schemas.user_schema import UserRegister, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db=Depends(get_database)) -> AuthService:
    """Dependency to get AuthService instance"""
    user_repo = UserRepository(db)
    event_repo = EventRepository(db)
    registration_repo = RegistrationRepository(db)
    return AuthService(user_repo, event_repo, registration_repo)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    - **name**: User's full name
    - **email**: User's email address
    - **password**: User's password (will be hashed)
    - **city**: User's city
    
    Returns a JWT token
    """
    return await auth_service.register(user_data)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns a JWT token
    """
    return await auth_service.login(credentials)
