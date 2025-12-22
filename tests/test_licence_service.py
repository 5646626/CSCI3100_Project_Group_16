"""
Tests for LicenceService.
Tests licence validation, creation, and redemption.
"""
import pytest
from services.licence_service import LicenceService
from repositories.licence_repository import LicenceRepository
from models.entities import Licence
from bson import ObjectId


class TestLicenceService:
    """Test suite for licence management functionality."""
    
    def test_validate_licence_format_valid(self):
        """Test valid licence key formats."""
        valid_keys = [
            "ABCD-1234-EFGH-5678",
            "TEST-TEST-TEST-TEST",
            "0000-0000-0000-0000",
            "ZZZZ-9999-AAAA-1111"
        ]
        
        for key in valid_keys:
            assert LicenceService._is_valid_format(key) is True
    
    def test_validate_licence_format_invalid(self):
        """Test invalid licence key formats."""
        invalid_keys = [
            "ABC-1234-EFGH-5678",  # Too short
            "ABCDE-1234-EFGH-5678",  # Too long
            "ABCD-1234-EFGH",  # Missing part
            "ABCD-1234-EFGH-5678-9999",  # Too many parts
            "ABCD_1234_EFGH_5678",  # Wrong separator
            "ABCD-12 4-EFGH-5678",  # Contains space
            "ABCD-12$4-EFGH-5678",  # Contains special char
            ""  # Empty string
        ]
        
        for key in invalid_keys:
            assert LicenceService._is_valid_format(key) is False
    
    def test_validate_licence_success(self, licence_repo):
        """Test validating an existing unclaimed licence."""
        # Arrange
        licence = Licence(key="VALD-1234-5678-ABCD", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act
        result = licence_service.validate_licence("VALD-1234-5678-ABCD")
        
        # Assert
        assert result is True
    
    def test_validate_licence_invalid_format(self, licence_repo):
        """Test validating licence with invalid format."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid licence format"):
            licence_service.validate_licence("INVALID")
    
    def test_get_redeemable_licence_success(self, licence_repo):
        """Test getting an unclaimed licence."""
        # Arrange
        licence = Licence(key="REDM-1234-5678-ABCD", owner_id=None, role="Hashira")
        licence_repo.create_licence(licence)
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act
        result = licence_service.get_redeemable_licence("REDM-1234-5678-ABCD")
        
        # Assert
        assert result is not None
        assert result.key == "REDM-1234-5678-ABCD"
        assert result.role == "Hashira"
        assert result.owner_id is None
    
    def test_get_redeemable_licence_invalid_format(self, licence_repo):
        """Test getting licence with invalid format."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid licence format"):
            licence_service.get_redeemable_licence("INVALID")
    
    def test_get_redeemable_licence_not_found(self, licence_repo):
        """Test getting non-existent licence."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            licence_service.get_redeemable_licence("NOTA-1234-5678-ABCD")
    
    def test_get_redeemable_licence_already_used(self, licence_repo):
        """Test getting licence that's already been claimed."""
        # Arrange
        owner_id = ObjectId()
        licence = Licence(key="USED-1234-5678-ABCD", owner_id=owner_id, role="Members")
        licence_repo.create_licence(licence)
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="already been used"):
            licence_service.get_redeemable_licence("USED-1234-5678-ABCD")
    
    def test_redeem_licence_success(self, licence_repo):
        """Test successfully redeeming a licence."""
        # Arrange
        licence = Licence(key="REDM-1111-2222-3333", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        licence_service = LicenceService(licence_repo=licence_repo)
        user_id = ObjectId()
        
        # Act
        licence_service.redeem_licence("REDM-1111-2222-3333", user_id)
        
        # Assert
        claimed_licence = licence_repo.find_licence_by_key("REDM-1111-2222-3333")
        assert claimed_licence.owner_id == user_id
    
    def test_redeem_licence_fail_already_claimed(self, licence_repo):
        """Test redeeming licence that's already claimed."""
        # Arrange
        existing_owner = ObjectId()
        licence = Licence(key="CLMD-1111-2222-3333", owner_id=existing_owner, role="Members")
        licence_repo.create_licence(licence)
        licence_service = LicenceService(licence_repo=licence_repo)
        new_user_id = ObjectId()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to claim"):
            licence_service.redeem_licence("CLMD-1111-2222-3333", new_user_id)
    
    def test_create_licence_success_members(self, licence_repo):
        """Test creating a Members licence."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act
        licence_id = licence_service.create_licence("NEWM-1111-2222-3333", role="Members")
        
        # Assert
        assert licence_id is not None
        licence = licence_repo.find_licence_by_key("NEWM-1111-2222-3333")
        assert licence.role == "Members"
        assert licence.owner_id is None
    
    def test_create_licence_success_hashira(self, licence_repo):
        """Test creating a Hashira licence."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act
        licence_id = licence_service.create_licence("NEWH-1111-2222-3333", role="Hashira")
        
        # Assert
        licence = licence_repo.find_licence_by_key("NEWH-1111-2222-3333")
        assert licence.role == "Hashira"
    
    def test_create_licence_success_boss(self, licence_repo):
        """Test creating a Boss licence."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act
        licence_id = licence_service.create_licence("NEWB-1111-2222-3333", role="Boss")
        
        # Assert
        licence = licence_repo.find_licence_by_key("NEWB-1111-2222-3333")
        assert licence.role == "Boss"
    
    def test_create_licence_invalid_format(self, licence_repo):
        """Test creating licence with invalid format."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid licence format"):
            licence_service.create_licence("INVALID", role="Members")
    
    def test_create_licence_invalid_role(self, licence_repo):
        """Test creating licence with invalid role."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid role"):
            licence_service.create_licence("NEWL-1111-2222-3333", role="InvalidRole")
    
    def test_licence_lifecycle(self, licence_repo):
        """Test complete licence lifecycle: create, validate, redeem."""
        # Arrange
        licence_service = LicenceService(licence_repo=licence_repo)
        
        # Create
        licence_id = licence_service.create_licence("LIFE-1111-2222-3333", role="Members")
        assert licence_id is not None
        
        # Validate format
        assert licence_service.validate_licence("LIFE-1111-2222-3333") is True
        
        # Get redeemable
        licence = licence_service.get_redeemable_licence("LIFE-1111-2222-3333")
        assert licence.owner_id is None
        
        # Redeem
        user_id = ObjectId()
        licence_service.redeem_licence("LIFE-1111-2222-3333", user_id)
        
        # Verify claimed
        claimed = licence_repo.find_licence_by_key("LIFE-1111-2222-3333")
        assert claimed.owner_id == user_id
        
        # Cannot redeem again
        with pytest.raises(ValueError):
            licence_service.get_redeemable_licence("LIFE-1111-2222-3333")
