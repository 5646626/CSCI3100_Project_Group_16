from repositories.board_repository import BoardRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from models.entities import Board
from models.base_user import Boss
from bson import ObjectId

# ---------------Board Service-----------------#
class BoardService:

    def __init__(self, board_repo: BoardRepository = None, task_repo: TaskRepository = None, user_repo: UserRepository = None):
        self.board_repo = board_repo or BoardRepository()
        self.task_repo = task_repo or TaskRepository()
        self.user_repo = user_repo or UserRepository()
    
    def create_board(self, name: str, owner_id: ObjectId, user_role: str) -> ObjectId:
        # Ensure that only the Boss can create boards
        if user_role != "Boss":
            raise PermissionError(f"User role '{user_role}' cannot create boards. Only 'Boss' can.")
        
        if self.board_repo.find_board_by_name(name, owner_id):
            raise ValueError(f"Board '{name}' already exists")
        
        board = Board(name=name, owner_id=owner_id)
        return self.board_repo.create_board(board)
    
    # Get the board by board_id
    def get_board(self, board_id: ObjectId) -> Board:
        return self.board_repo.find_board_by_id(board_id)

    # Get the board by board_name
    def get_board_by_name(self, name: str, owner_id: ObjectId) -> Board:
        board = self.board_repo.find_board_by_name(name, owner_id)
        if not board:
            raise ValueError(f"Board '{name}' not found for this user")
        return board

    # Get the board by name that is visible to the current user
    # All user roles can view boards created by Boss users
    # Can be expanded in the future for more complex visibility rules
    def get_board_visible_to_user(self, name: str, user_id: ObjectId, user_role: str) -> Board:

        # All user roles: look up boards by name, but only those owned by Boss users
        candidate_boards = self.board_repo.find_boards_by_name(name)
        if not candidate_boards:
            raise ValueError(f"Board '{name}' not found")

        # Filter to boards whose owner has role Boss
        boss_owned = []
        for b in candidate_boards:
            owner = self.user_repo.find_user_by_id(b.owner_id)
            if owner and getattr(owner, "role", "Members") == "Boss":
                boss_owned.append(b)

        if not boss_owned:
            raise PermissionError("You can only view boards created by a Boss")

        # If multiple boards have the same name across different Boss owners, return the first deterministically
        return boss_owned[0]
    
    # List all boards visible to the user
    def list_boards_for_user(self, user_id: ObjectId, user_role: str) -> list:

        # All user roles: list all boards owned by Boss users
        boss_users = self.user_repo.find_user_by_role("Boss")
        boss_ids = {u._id for u in boss_users if getattr(u, "_id", None)}
        visible_boards = []
        for boss_id in boss_ids:
            visible_boards.extend(self.board_repo.find_board_by_owner(boss_id))
        return visible_boards
    
    # Delete a board by name
    def delete_board(self, board_name: str, owner_id: ObjectId, user_role: str) -> bool:
        if user_role != "Boss":
            raise PermissionError(f"User role '{user_role}' cannot delete boards. Only 'Boss' can.")

        board = self.get_board_by_name(board_name, owner_id)

        tasks = self.task_repo.find_task_by_board(board._id)
        for task in tasks:
            self.task_repo.delete_task(task._id)

        return self.board_repo.delete_board(board._id)
    
#----------Not currenly used, but could implemented in the future----------#
#   Add a column to the board
#   def add_column(self, board_id: ObjectId, column_name: str) -> bool:
#     board = self.board_repo.find_board_by_id(board_id)
#     if not board:
#         raise ValueError("Board not found")
#
#     normalized_column = column_name.upper()
#
#     if normalized_column in board.columns:
#       raise ValueError(f"Column '{column_name}' already exists")
#     
#     if len(board.columns) >= 10:
#       raise ValueError("Maximum 10 columns per board")
#  
#    board.columns.append(normalized_column)
#    return self.board_repo.update_board(board_id, {"columns": board.columns})