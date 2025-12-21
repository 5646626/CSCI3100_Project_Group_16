from repositories.licence_repository import LicenceRepository
from models.entities import Licence
from bson import ObjectId

class LicenceService:
    """Service for licence management."""
    
    VALID_FORMAT = "AAAA-BBBB-CCCC-DDDD"
    
    def __init__(self, licence_repo: LicenceRepository = None):
        self.licence_repo = licence_repo or LicenceRepository()
    
    def validate_licence(self, key: str) -> bool:
        """Check if licence key is valid."""
        if not self._is_valid_format(key):
            raise ValueError(f"Invalid licence format. Expected: {self.VALID_FORMAT}")
        
        return self.licence_repo.validate_licence(key)
    
    def validate_licence_file(self, file_path: str) -> str:
        """Read and validate licence from file."""
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
    
    def create_licence(self, key: str, owner_id: ObjectId) -> ObjectId:
        """Create a new licence for a user."""
        if not self._is_valid_format(key):
            raise ValueError(f"Invalid licence format. Expected: {self.VALID_FORMAT}")
        
        licence = Licence(key=key, owner_id=owner_id)
        return self.licence_repo.create_licence(licence)
    
    @staticmethod
    def _is_valid_format(key: str) -> bool:
        """Check licence key format AAAA-BBBB-CCCC-DDDD."""
        parts = key.split('-')
        if len(parts) != 4:
            return False
        return all(len(part) == 4 and part.isalnum() for part in parts)