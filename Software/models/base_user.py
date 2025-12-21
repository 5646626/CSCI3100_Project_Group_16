from bson import ObjectId

#----------------User Classes-----------------#
# Members can view boards and list boards
class Members:
    role = "Members"

    def __init__(self, username: str, password_hash: str, email: str, role: str = "Members", _id: ObjectId = None):
        self._id = _id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        # Persist the role explicitly so restored documents and subclasses stay aligned
        self.role = role or self.role

    def view_boards(self) -> list:
        return []  #To be populated by repository
    
    def list_boards(self) -> list:
        return []  #To be populated by repository
    
    # Convert to MongoDB document
    def to_dict(self):
        result = {
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "role": self.role,
        }
        if self._id is not None:
            result["_id"] = self._id
        return result

# Hashira can manage tasks (edit, create, delete, move) and inherits all Members permissions
class Hashira(Members):
    role: str = "Hashira"

    def __init__(self, username: str, password_hash: str, email: str, role: str = None, _id: ObjectId = None):
        # Accept role parameter but always use our class-level role
        super().__init__(username=username, password_hash=password_hash, email=email, role=self.role, _id=_id)

    def create_task(self, title: str, board_id: ObjectId, column: str) -> bool:
        return True  # Implemented in service layer
    
    def edit_task(self, task_id: ObjectId, updates: dict) -> bool:
        return True  # Implemented in service layer
    
    def delete_task(self, task_id: ObjectId) -> bool:
        return True  # Implemented in service layer
    
    def move_task_to_todo(self, task_id: ObjectId) -> bool:
        return True  # Implemented in service layer
    
    def move_task_to_doing(self, task_id: ObjectId) -> bool:
        return True  # Implemented in service layer
    
    def move_task_to_done(self, task_id: ObjectId) -> bool:
        return True  # Implemented in service layer

# Boss can manage boards (create, delete) and inherits all Hashira permissions
class Boss(Hashira):
    role: str = "Boss"

    def __init__(self, username: str, password_hash: str, email: str, role: str = None, _id: ObjectId = None):
        # Accept role parameter but always use our class-level role
        super().__init__(username=username, password_hash=password_hash, email=email, role=self.role, _id=_id)

    def create_board(self, name: str) -> bool:
        return True  # Implemented in service layer
    
    def delete_board(self, board_id: ObjectId) -> bool:
        return True  # Implemented in service layer