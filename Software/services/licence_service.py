from repositories.licence_repository import LicenceRepository
from models.entities import Licence
from bson import ObjectId

#----------------Licence Service-----------------#
class LicenceService:
    
    VALID_FORMAT = "AAAA-BBBB-CCCC-DDDD"
    
    def __init__(self, licence_repo: LicenceRepository = None):
        self.licence_repo = licence_repo or LicenceRepository()
    
    # Check if licence key is valid
    def validate_licence(self, key: str) -> bool:
        if not self._is_valid_format(key):
            raise ValueError(f"Invalid licence format. Expected: {self.VALID_FORMAT}")
        
        return self.licence_repo.validate_licence(key)

    # Fetch a licence that exists but is not yet claimed
    def get_redeemable_licence(self, key: str) -> Licence:
        if not self._is_valid_format(key):
            raise ValueError(f"Invalid licence format. Expected: {self.VALID_FORMAT}")

        licence = self.licence_repo.find_licence_by_key(key)
        if not licence:
            raise ValueError("Licence key not found")
        if licence.owner_id is not None:
            raise ValueError("Licence key has already been used")

        return licence
    
    # Not currently used, but could be useful for file-based licence validation
    def validate_licence_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                key = f.read().strip()
            
            if self.validate_licence(key):
                return key
            else:
                raise ValueError("Licence key in file is not valid")
        except FileNotFoundError:
            raise FileNotFoundError(f"Licence file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading licence file: {e}")
    
    # Not currently used, but could be useful for creating licences in the future
    def create_licence(self, key: str, owner_id: ObjectId | None = None, role: str = "Members") -> ObjectId:
        if not self._is_valid_format(key):
            raise ValueError(f"Invalid licence format. Expected: {self.VALID_FORMAT}")

        valid_roles = ["Members", "Hashira", "Boss"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        
        licence = Licence(key=key, owner_id=owner_id, role=role)
        return self.licence_repo.create_licence(licence)

    def redeem_licence(self, key: str, owner_id: ObjectId) -> None:
        """Mark a licence as claimed by a specific user."""
        updated = self.licence_repo.assign_owner(key, owner_id)
        if not updated:
            raise ValueError("Failed to claim licence key; it may have been used")
    
    #----------------Helper Functions-----------------#
    @staticmethod
    def _is_valid_format(key: str) -> bool:
        """Check licence key format AAAA-BBBB-CCCC-DDDD."""
        parts = key.split('-')
        if len(parts) != 4:
            return False
        return all(len(part) == 4 and part.isalnum() for part in parts)