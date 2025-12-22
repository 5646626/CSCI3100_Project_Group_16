"""
Tests for BoardService.
Tests board creation, listing, viewing, and deletion with role-based permissions.
"""
import pytest
from services.board_services import BoardService
from repositories.board_repository import BoardRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from models.entities import Board, Task
from bson import ObjectId


class TestBoardService:
    """Test suite for board management functionality."""
    
    def test_create_board_success_boss(self, board_repo, task_repo, user_repo, sample_boss_user):
        """Test Boss can create a board successfully."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        board_id = board_service.create_board("New Board", sample_boss_user._id, "Boss")
        
        # Assert
        assert board_id is not None
        board = board_repo.find_board_by_id(board_id)
        assert board.name == "New Board"
        assert board.owner_id == sample_boss_user._id
        assert board.columns == ["TODO", "DOING", "DONE"]
    
    def test_create_board_fail_hashira(self, board_repo, task_repo, user_repo, sample_hashira_user):
        """Test Hashira cannot create boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot create boards"):
            board_service.create_board("New Board", sample_hashira_user._id, "Hashira")
    
    def test_create_board_fail_member(self, board_repo, task_repo, user_repo, sample_member_user):
        """Test Members cannot create boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot create boards"):
            board_service.create_board("New Board", sample_member_user._id, "Members")
    
    def test_create_board_fail_duplicate_name(self, board_repo, task_repo, user_repo, sample_boss_user, sample_board):
        """Test cannot create board with duplicate name for same owner."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            board_service.create_board(sample_board.name, sample_boss_user._id, "Boss")
    
    def test_get_board_by_id(self, board_repo, task_repo, user_repo, sample_board):
        """Test getting board by ID."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        board = board_service.get_board(sample_board._id)
        
        # Assert
        assert board is not None
        assert board._id == sample_board._id
        assert board.name == sample_board.name
    
    def test_get_board_by_name(self, board_repo, task_repo, user_repo, sample_board, sample_boss_user):
        """Test getting board by name."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        board = board_service.get_board_by_name(sample_board.name, sample_boss_user._id)
        
        # Assert
        assert board is not None
        assert board.name == sample_board.name
    
    def test_get_board_by_name_not_found(self, board_repo, task_repo, user_repo, sample_boss_user):
        """Test getting non-existent board by name."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            board_service.get_board_by_name("Nonexistent Board", sample_boss_user._id)
    
    def test_get_board_visible_to_user_boss(self, board_repo, task_repo, user_repo, sample_board, sample_boss_user):
        """Test Boss can view Boss-owned boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        board = board_service.get_board_visible_to_user(sample_board.name, sample_boss_user._id, "Boss")
        
        # Assert
        assert board is not None
        assert board.name == sample_board.name
    
    def test_get_board_visible_to_user_member(self, board_repo, task_repo, user_repo, sample_board, sample_member_user):
        """Test Members can view Boss-owned boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        board = board_service.get_board_visible_to_user(sample_board.name, sample_member_user._id, "Members")
        
        # Assert
        assert board is not None
        assert board.name == sample_board.name
    
    def test_get_board_visible_fail_not_found(self, board_repo, task_repo, user_repo, sample_member_user):
        """Test viewing non-existent board fails."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            board_service.get_board_visible_to_user("Nonexistent", sample_member_user._id, "Members")
    
    def test_list_boards_for_boss(self, board_repo, task_repo, user_repo, sample_boss_user):
        """Test Boss can list all Boss-owned boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        board1_id = board_service.create_board("Board 1", sample_boss_user._id, "Boss")
        board2_id = board_service.create_board("Board 2", sample_boss_user._id, "Boss")
        
        # Act
        boards = board_service.list_boards_for_user(sample_boss_user._id, "Boss")
        
        # Assert
        assert len(boards) == 2
        board_names = [b.name for b in boards]
        assert "Board 1" in board_names
        assert "Board 2" in board_names
    
    def test_list_boards_for_member(self, board_repo, task_repo, user_repo, sample_boss_user, sample_member_user):
        """Test Members can list all Boss-owned boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        board_service.create_board("Board 1", sample_boss_user._id, "Boss")
        board_service.create_board("Board 2", sample_boss_user._id, "Boss")
        
        # Act
        boards = board_service.list_boards_for_user(sample_member_user._id, "Members")
        
        # Assert
        assert len(boards) == 2
    
    def test_list_boards_empty(self, board_repo, task_repo, user_repo, sample_member_user):
        """Test listing boards when none exist."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        boards = board_service.list_boards_for_user(sample_member_user._id, "Members")
        
        # Assert
        assert len(boards) == 0
    
    def test_delete_board_success_boss(self, board_repo, task_repo, user_repo, sample_boss_user, sample_board):
        """Test Boss can delete their own boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        result = board_service.delete_board(sample_board.name, sample_boss_user._id, "Boss")
        
        # Assert
        assert result is True
        board = board_repo.find_board_by_id(sample_board._id)
        assert board is None
    
    def test_delete_board_with_tasks(self, board_repo, task_repo, user_repo, sample_boss_user, sample_board):
        """Test deleting board also deletes associated tasks."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Create tasks on the board
        task1 = Task(title="Task 1", board_id=sample_board._id, column="TODO")
        task2 = Task(title="Task 2", board_id=sample_board._id, column="DOING")
        task_repo.create_task(task1)
        task_repo.create_task(task2)
        
        # Act
        result = board_service.delete_board(sample_board.name, sample_boss_user._id, "Boss")
        
        # Assert
        assert result is True
        tasks = task_repo.find_task_by_board(sample_board._id)
        assert len(tasks) == 0
    
    def test_delete_board_fail_hashira(self, board_repo, task_repo, user_repo, sample_boss_user, sample_board, sample_hashira_user):
        """Test Hashira cannot delete boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot delete boards"):
            board_service.delete_board(sample_board.name, sample_hashira_user._id, "Hashira")
    
    def test_delete_board_fail_member(self, board_repo, task_repo, user_repo, sample_boss_user, sample_board, sample_member_user):
        """Test Members cannot delete boards."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot delete boards"):
            board_service.delete_board(sample_board.name, sample_member_user._id, "Members")
    
    def test_board_default_columns(self, board_repo, task_repo, user_repo, sample_boss_user):
        """Test boards are created with default columns."""
        # Arrange
        board_service = BoardService(board_repo=board_repo, task_repo=task_repo, user_repo=user_repo)
        
        # Act
        board_id = board_service.create_board("Test Board", sample_boss_user._id, "Boss")
        board = board_repo.find_board_by_id(board_id)
        
        # Assert
        assert board.columns == ["TODO", "DOING", "DONE"]
