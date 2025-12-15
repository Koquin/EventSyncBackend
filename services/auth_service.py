from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from schemas.user_schema import UserRegister, UserLogin, Token
from utils.auth import hash_password, verify_password, create_access_token
from utils.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from utils.debug import debug_print


class AuthService:
    def __init__(
        self, 
        user_repo: UserRepository,
        event_repo: EventRepository,
        registration_repo: RegistrationRepository
    ):
        self.user_repo = user_repo
        self.event_repo = event_repo
        self.registration_repo = registration_repo
    
    async def register(self, user_data: UserRegister) -> Token:
        """Register a new user"""
        debug_print("auth_service.py", "register", "variables", email=user_data.email, name=user_data.name)
        
        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            debug_print("auth_service.py", "register", "error", error="UserAlreadyExistsException", reason=f"User with email {user_data.email} already exists")
            raise UserAlreadyExistsException()
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        user_id = await self.user_repo.create_user(user_dict)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user_id})
        token = Token(token=access_token)
        
        debug_print("auth_service.py", "register", "returning", token=token)
        return token
    
    async def login(self, credentials: UserLogin) -> Token:
        """Login user"""
        debug_print("auth_service.py", "login", "variables", email=credentials.email, senha=credentials.password)
        
        # Find user by email
        user = await self.user_repo.get_user_by_email(credentials.email)
        if not user:
            debug_print("auth_service.py", "login", "error", error="InvalidCredentialsException", reason=f"User with email {credentials.email} not found")
            raise InvalidCredentialsException()
        
        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            debug_print("auth_service.py", "login", "error", error="InvalidCredentialsException", reason=f"Invalid password for user {credentials.email}")
            raise InvalidCredentialsException()
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user["id"]})
        token = Token(token=access_token)
        
        debug_print("auth_service.py", "login", "returning", token=token, user_id=user["id"])
        return token
