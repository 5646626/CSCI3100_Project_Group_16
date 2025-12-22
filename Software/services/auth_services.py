from repositories.user_repository import UserRepository
from services.licence_service import LicenceService
from models.base_user import Members, Hashira, Boss
from bson import ObjectId
import re

class AuthService:
    """Service for user authentication and role management."""
    
    def __init__(self, user_repo: UserRepository = None, licence_service: LicenceService = None):
        self.user_repo = user_repo or UserRepository()
        self.licence_service = licence_service or LicenceService()
    
    def signup(self, username: str, password: str, email: str = None, role: str = "Members", licence_key: str | None = None) -> tuple[ObjectId, str]:
        """Register a new user with a valid licence key (Members, Hashira, or Boss)."""
        # Check if user exists
        if self.user_repo.find_by_username(username):
            raise ValueError(f"User '{username}' already exists")

        if not licence_key:
            raise ValueError("Licence key is required to sign up")
        
        # Validate role
        valid_roles = ["Members", "Hashira", "Boss"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")

        licence = self.licence_service.get_redeemable_licence(licence_key)
        resolved_role = licence.role
        if role and resolved_role != role:
            raise ValueError(f"Licence role '{resolved_role}' does not match requested role '{role}'")

        # Validate email early to avoid DB validator errors
        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not email or not re.match(email_pattern, email):
            raise ValueError("Invalid or missing email. Please provide a valid email address.")
        
        # Create user with appropriate role class
        password_hash = UserRepository.hash_password(password)
        
        if resolved_role == "Boss":
            user = Boss(username=username, password_hash=password_hash, email=email, role=resolved_role)
        elif resolved_role == "Hashira":
            user = Hashira(username=username, password_hash=password_hash, email=email, role=resolved_role)
        else:
            user = Members(username=username, password_hash=password_hash, email=email, role=resolved_role)
        
        user_id = self.user_repo.create(user)
        self.licence_service.redeem_licence(licence_key, user_id)
        return user_id, resolved_role
    
    def login(self, username: str, password: str) -> Members:
        """Authenticate user and return user object with correct role."""
        user = self.user_repo.find_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        
        password_hash = UserRepository.hash_password(password)
        if user.password_hash != password_hash:
            raise ValueError("Invalid password")
        
        return user
    
    def get_user(self, username: str) -> Members:
        """Get user by username."""
        return self.user_repo.find_by_username(username)
    
    def promote_user(self, user_id: ObjectId, new_role: str) -> bool:
        """Promote/demote user to a different role."""
        return self.user_repo.update_user_role(user_id, new_role)