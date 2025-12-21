from repositories.board_repository import BoardRepository
from repositories.task_repository import TaskRepository
from models.entities import Board
from models.base_user import Boss
from bson import ObjectId

class BoardService:
    """Service for board management with role-based access control."""
    
    def __init__(self, board_repo: BoardRepository = None, task_repo: TaskRepository = None):
        self.board_repo = board_repo or BoardRepository()
        self.task_repo = task_repo or TaskRepository()
    
    def create_board(self, name: str, owner_id: ObjectId, user_role: str) -> ObjectId:
        """Only Boss role can create boards."""
        if user_role != "Boss":
            raise PermissionError(f"User role '{user_role}' cannot create boards. Only 'Boss' can.")
        
        if self.board_repo.find_by_name(name, owner_id):
            raise ValueError(f"Board '{name}' already exists")
        
        board = Board(name=name, owner_id=owner_id)
        return self.board_repo.create(board)
    
    def get_board(self, board_id: ObjectId) -> Board:
        """Get board by ID."""
        return self.board_repo.find_by_id(board_id)

    def get_board_by_name(self, name: str, owner_id: ObjectId) -> Board:
        """Resolve a board by its name for a specific owner."""
        board = self.board_repo.find_by_name(name, owner_id)
        if not board:
            raise ValueError(f"Board '{name}' not found for this user")
        return board
    
    def list_boards(self, owner_id: ObjectId) -> list:
        """List all boards for a user (Members, Hashira, Boss can view)."""
        return self.board_repo.find_by_owner(owner_id)
    
    def add_column(self, board_id: ObjectId, column_name: str) -> bool:
        """Add a column to board."""
        board = self.board_repo.find_by_id(board_id)
        if not board:
            raise ValueError("Board not found")

        normalized_column = column_name.upper()

        if normalized_column in board.columns:
            raise ValueError(f"Column '{column_name}' already exists")
        
        if len(board.columns) >= 10:
            raise ValueError("Maximum 10 columns per board")
        
        board.columns.append(normalized_column)
        return self.board_repo.update(board_id, {"columns": board.columns})
    
    def delete_board(self, board_name: str, owner_id: ObjectId, user_role: str) -> bool:
        """Only Boss role can delete boards."""
        if user_role != "Boss":
            raise PermissionError(f"User role '{user_role}' cannot delete boards. Only 'Boss' can.")

        board = self.get_board_by_name(board_name, owner_id)

        tasks = self.task_repo.find_by_board(board._id)
        for task in tasks:
            self.task_repo.delete(task._id)

        return self.board_repo.delete(board._id)