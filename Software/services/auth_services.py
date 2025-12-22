from repositories.user_repository import UserRepository
from services.licence_service import LicenceService
from models.base_user import Members, Hashira, Boss
from bson import ObjectId
import re

#---------------Authentication Service-----------------#
class AuthService:
    
    def __init__(self, user_repo: UserRepository = None, licence_service: LicenceService = None):
        self.user_repo = user_repo or UserRepository()
        self.licence_service = licence_service or LicenceService()
    
    # Register a new user with a valid licence key (Members, Hashira, or Boss).
    def signup(self, username: str, password: str, email: str = None, role: str = "Members", licence_key: str | None = None) -> tuple[ObjectId, str]:
        # Although we have the Schema, we do one more pre-validation here for fast catching errors

        # Check if user exists
        if self.user_repo.find_user_by_username(username):
            raise ValueError(f"User '{username}' already exists")
        
        # Check if licence key exists
        if not licence_key:
            raise ValueError("Licence key is required to sign up")
        
        # Validate role
        valid_roles = ["Members", "Hashira", "Boss"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        
        # Validate licence
        licence = self.licence_service.get_redeemable_licence(licence_key)
        resolved_role = licence.role
        if role and resolved_role != role:
            raise ValueError(f"Licence role '{resolved_role}' does not match requested role '{role}'")

        # Validate email early to avoid DB validator errors
        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not email or not re.match(email_pattern, email):
            raise ValueError("Invalid or missing email. Please provide a valid email address.")
        
        # Create user with the role class
        password_hash = UserRepository.hash_password(password)
        
        if resolved_role == "Boss":
            user = Boss(username=username, password_hash=password_hash, email=email, role=resolved_role)
        elif resolved_role == "Hashira":
            user = Hashira(username=username, password_hash=password_hash, email=email, role=resolved_role)
        else:
            user = Members(username=username, password_hash=password_hash, email=email, role=resolved_role)
        
        user_id = self.user_repo.create_new_user(user)
        self.licence_service.redeem_licence(licence_key, user_id)
        return user_id, resolved_role
    
    # Login user and return user object
    def login(self, username: str, password: str) -> Members:
        user = self.user_repo.find_user_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        
        password_hash = UserRepository.hash_password(password)
        if user.password_hash != password_hash:
            raise ValueError("Invalid password")
        
        return user
    
    # Get user by username
    def get_user(self, username: str) -> Members:
        # Get user by username
        return self.user_repo.find_user_by_username(username)
    
#----------Not currenly used, but could implemented in the future----------#
#   Update user to a different role
#   def promote_user_role(self, user_id: ObjectId, new_role: str) -> bool:
#       return self.user_repo.update_user_role(user_id, new_role)