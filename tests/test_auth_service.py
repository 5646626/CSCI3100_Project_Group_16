"""
Tests for AuthService.
Tests user registration, login, and role management.
"""
import pytest
from services.auth_services import AuthService
from repositories.user_repository import UserRepository
from services.licence_service import LicenceService
from models.entities import Licence
from bson import ObjectId


class TestAuthService:
    """Test suite for authentication functionality."""
    
    def test_signup_success_member(self, user_repo, licence_repo):
        """Test successful signup with Members role."""
        # Arrange
        licence = Licence(key="MEMB-1234-5678-ABCD", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act
        user_id, role = auth_service.signup(
            username="newmember",
            password="secure123",
            email="newmember@test.com",
            role="Members",
            licence_key="MEMB-1234-5678-ABCD"
        )
        
        # Assert
        assert user_id is not None
        assert role == "Members"
        user = user_repo.find_user_by_id(user_id)
        assert user.username == "newmember"
        assert user.role == "Members"
    
    def test_signup_success_hashira(self, user_repo, licence_repo):
        """Test successful signup with Hashira role."""
        # Arrange
        licence = Licence(key="HASH-1234-5678-ABCD", owner_id=None, role="Hashira")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act
        user_id, role = auth_service.signup(
            username="newhashira",
            password="secure123",
            email="hashira@test.com",
            role="Hashira",
            licence_key="HASH-1234-5678-ABCD"
        )
        
        # Assert
        assert role == "Hashira"
        user = user_repo.find_user_by_id(user_id)
        assert user.role == "Hashira"
    
    def test_signup_success_boss(self, user_repo, licence_repo):
        """Test successful signup with Boss role."""
        # Arrange
        licence = Licence(key="BOSS-1234-5678-ABCD", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act
        user_id, role = auth_service.signup(
            username="newboss",
            password="secure123",
            email="boss@test.com",
            role="Boss",
            licence_key="BOSS-1234-5678-ABCD"
        )
        
        # Assert
        assert role == "Boss"
        user = user_repo.find_user_by_id(user_id)
        assert user.role == "Boss"
    
    def test_signup_fail_duplicate_username(self, user_repo, licence_repo, sample_member_user):
        """Test signup fails with duplicate username."""
        # Arrange
        licence = Licence(key="MEMB-1234-5678-ABCD", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            auth_service.signup(
                username=sample_member_user.username,
                password="password123",
                email="another@test.com",
                role="Members",
                licence_key="MEMB-1234-5678-ABCD"
            )
    
    def test_signup_fail_missing_licence_key(self, user_repo, licence_repo):
        """Test signup fails without licence key."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act & Assert
        with pytest.raises(ValueError, match="Licence key is required"):
            auth_service.signup(
                username="newuser",
                password="password123",
                email="user@test.com",
                role="Members",
                licence_key=None
            )
    
    def test_signup_fail_invalid_role(self, user_repo, licence_repo):
        """Test signup fails with invalid role."""
        # Arrange
        licence = Licence(key="MEMB-1234-5678-ABCD", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid role"):
            auth_service.signup(
                username="newuser",
                password="password123",
                email="user@test.com",
                role="InvalidRole",
                licence_key="MEMB-1234-5678-ABCD"
            )
    
    def test_signup_fail_role_mismatch(self, user_repo, licence_repo):
        """Test signup fails when requested role doesn't match licence role."""
        # Arrange
        licence = Licence(key="MEMB-1234-5678-ABCD", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act & Assert
        with pytest.raises(ValueError, match="does not match requested role"):
            auth_service.signup(
                username="newuser",
                password="password123",
                email="user@test.com",
                role="Boss",
                licence_key="MEMB-1234-5678-ABCD"
            )
    
    def test_signup_fail_invalid_email(self, user_repo, licence_repo):
        """Test signup fails with invalid email format."""
        # Arrange
        licence = Licence(key="MEMB-1234-5678-ABCD", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid or missing email"):
            auth_service.signup(
                username="newuser",
                password="password123",
                email="invalid-email",
                role="Members",
                licence_key="MEMB-1234-5678-ABCD"
            )
    
    def test_signup_fail_used_licence(self, user_repo, licence_repo):
        """Test signup fails with already used licence key."""
        # Arrange
        existing_user_id = ObjectId()
        licence = Licence(key="MEMB-1234-5678-ABCD", owner_id=existing_user_id, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Act & Assert
        with pytest.raises(ValueError, match="already been used"):
            auth_service.signup(
                username="newuser",
                password="password123",
                email="user@test.com",
                role="Members",
                licence_key="MEMB-1234-5678-ABCD"
            )
    
    def test_login_success(self, user_repo, sample_member_user):
        """Test successful login."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo)
        
        # Act
        logged_in_user = auth_service.login(sample_member_user.username, "password123")
        
        # Assert
        assert logged_in_user is not None
        assert logged_in_user.username == sample_member_user.username
        assert logged_in_user._id == sample_member_user._id
    
    def test_login_fail_wrong_password(self, user_repo, sample_member_user):
        """Test login fails with wrong password."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid password"):
            auth_service.login(sample_member_user.username, "wrongpassword")
    
    def test_login_fail_user_not_found(self, user_repo):
        """Test login fails with non-existent user."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            auth_service.login("nonexistent", "password123")
    
    def test_get_user_success(self, user_repo, sample_member_user):
        """Test getting user by username."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo)
        
        # Act
        user = auth_service.get_user(sample_member_user.username)
        
        # Assert
        assert user is not None
        assert user.username == sample_member_user.username
    
    def test_get_user_not_found(self, user_repo):
        """Test getting non-existent user returns None."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo)
        
        # Act
        user = auth_service.get_user("nonexistent")
        
        # Assert
        assert user is None
    
    def test_password_hashing_consistency(self):
        """Test password hashing produces consistent results."""
        # Arrange
        password = "testpassword123"
        
        # Act
        hash1 = UserRepository.hash_password(password)
        hash2 = UserRepository.hash_password(password)
        
        # Assert
        assert hash1 == hash2
    
    def test_password_hashing_different_passwords(self):
        """Test different passwords produce different hashes."""
        # Arrange
        password1 = "password1"
        password2 = "password2"
        
        # Act
        hash1 = UserRepository.hash_password(password1)
        hash2 = UserRepository.hash_password(password2)
        
        # Assert
        assert hash1 != hash2
