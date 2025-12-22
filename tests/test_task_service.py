"""
Tests for TaskService.
Tests task creation, editing, moving, and deletion with role-based permissions.
"""
import pytest
from services.task_service import TaskService
from repositories.task_repository import TaskRepository
from models.entities import Task
from bson import ObjectId


class TestTaskService:
    """Test suite for task management functionality."""
    
    def test_create_task_success_boss(self, task_repo, sample_board, sample_boss_user):
        """Test Boss can create tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        task_id = task_service.create_task(
            title="New Task",
            board_id=sample_board._id,
            column="TODO",
            user_role="Boss",
            description="Test description",
            priority="high"
        )
        
        # Assert
        assert task_id is not None
        task = task_repo.find_task_by_id(task_id)
        assert task.title == "New Task"
        assert task.column == "TODO"
        assert task.priority == "high"
    
    def test_create_task_success_hashira(self, task_repo, sample_board, sample_hashira_user):
        """Test Hashira can create tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        task_id = task_service.create_task(
            title="Hashira Task",
            board_id=sample_board._id,
            column="DOING",
            user_role="Hashira",
            priority="medium"
        )
        
        # Assert
        assert task_id is not None
        task = task_repo.find_task_by_id(task_id)
        assert task.title == "Hashira Task"
        assert task.column == "DOING"
    
    def test_create_task_fail_member(self, task_repo, sample_board, sample_member_user):
        """Test Members cannot create tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot create tasks"):
            task_service.create_task(
                title="Member Task",
                board_id=sample_board._id,
                column="TODO",
                user_role="Members"
            )
    
    def test_create_task_with_default_priority(self, task_repo, sample_board):
        """Test task creation with default priority."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        task_id = task_service.create_task(
            title="Default Priority Task",
            board_id=sample_board._id,
            column="TODO",
            user_role="Boss"
        )
        
        # Assert
        task = task_repo.find_task_by_id(task_id)
        assert task.priority == "medium"
    
    def test_create_task_invalid_priority(self, task_repo, sample_board):
        """Test task creation fails with invalid priority."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Priority must be"):
            task_service.create_task(
                title="Invalid Priority Task",
                board_id=sample_board._id,
                column="TODO",
                user_role="Boss",
                priority="urgent"
            )
    
    def test_create_task_all_priorities(self, task_repo, sample_board):
        """Test task creation with all valid priorities."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        priorities = ["high", "medium", "low"]
        
        # Act & Assert
        for priority in priorities:
            task_id = task_service.create_task(
                title=f"Task {priority}",
                board_id=sample_board._id,
                column="TODO",
                user_role="Boss",
                priority=priority
            )
            task = task_repo.find_task_by_id(task_id)
            assert task.priority == priority
    
    def test_get_task_by_id(self, task_repo, sample_task):
        """Test getting task by ID."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        task = task_service.get_task_by_id(sample_task._id)
        
        # Assert
        assert task is not None
        assert task._id == sample_task._id
        assert task.title == sample_task.title
    
    def test_list_tasks_in_column(self, task_repo, sample_board):
        """Test listing tasks in a specific column."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        task_service.create_task("Task 1", sample_board._id, "TODO", "Boss")
        task_service.create_task("Task 2", sample_board._id, "TODO", "Boss")
        task_service.create_task("Task 3", sample_board._id, "DOING", "Boss")
        
        # Act
        todo_tasks = task_service.list_tasks_in_column(sample_board._id, "TODO")
        doing_tasks = task_service.list_tasks_in_column(sample_board._id, "DOING")
        
        # Assert
        assert len(todo_tasks) == 2
        assert len(doing_tasks) == 1

    def test_edit_task_success_boss(self, task_repo, sample_task):
        """Test Boss can edit tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        updates = {
            "title": "Updated Title",
            "description": "Updated description",
            "priority": "high"
        }
        
        # Act
        result = task_service.edit_task(sample_task._id, updates, "Boss")
        
        # Assert
        assert result is True
        task = task_repo.find_task_by_id(sample_task._id)
        assert task.title == "Updated Title"
        assert task.description == "Updated description"
        assert task.priority == "high"
    
    def test_edit_task_success_hashira(self, task_repo, sample_task):
        """Test Hashira can edit tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        updates = {
            "title": "Hashira Updated",
            "description": "Updated description",
            "priority": "high"
        }
        
        # Act
        result = task_service.edit_task(sample_task._id, updates, "Hashira")
        
        # Assert
        assert result is True
        task = task_repo.find_task_by_id(sample_task._id)
        assert task.title == "Hashira Updated"
        assert task.description == "Updated description"
        assert task.priority == "high"

    
    def test_edit_task_fail_member(self, task_repo, sample_task):
        """Test Members cannot edit tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        updates = {"title": "Member Updated"}
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot edit tasks"):
            task_service.edit_task(sample_task._id, updates, "Members")
    
    def test_move_task_success_boss(self, task_repo, sample_task):
        """Test Boss can move tasks between columns."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        result = task_service.move_task(sample_task._id, "DOING", "Boss")
        
        # Assert
        assert result is True
        task = task_repo.find_task_by_id(sample_task._id)
        assert task.column == "DOING"
    
    def test_move_task_success_hashira(self, task_repo, sample_task):
        """Test Hashira can move tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        result = task_service.move_task(sample_task._id, "DONE", "Hashira")
        
        # Assert
        assert result is True
        task = task_repo.find_task_by_id(sample_task._id)
        assert task.column == "DONE"
    
    def test_move_task_fail_member(self, task_repo, sample_task):
        """Test Members cannot move tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot move tasks"):
            task_service.move_task(sample_task._id, "DOING", "Members")
    
    def test_move_task_invalid_column(self, task_repo, sample_task):
        """Test moving task to invalid column fails."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid column"):
            task_service.move_task(sample_task._id, "INVALID", "Boss")

    def test_delete_task_success_boss(self, task_repo, sample_task):
        """Test Boss can delete tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        result = task_service.delete_task(sample_task._id, "Boss")
        
        # Assert
        assert result is True
        task = task_repo.find_task_by_id(sample_task._id)
        assert task is None
    
    def test_delete_task_success_hashira(self, task_repo, sample_task):
        """Test Hashira can delete tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act
        result = task_service.delete_task(sample_task._id, "Hashira")
        
        # Assert
        assert result is True
        task = task_repo.find_task_by_id(sample_task._id)
        assert task is None
    
    def test_delete_task_fail_member(self, task_repo, sample_task):
        """Test Members cannot delete tasks."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Act & Assert
        with pytest.raises(PermissionError, match="cannot delete tasks"):
            task_service.delete_task(sample_task._id, "Members")
    
    def test_task_workflow(self, task_repo, sample_board):
        """Test complete task workflow: create, edit, move, delete."""
        # Arrange
        task_service = TaskService(task_repo=task_repo)
        
        # Create
        task_id = task_service.create_task("Workflow Task", sample_board._id, "TODO", "Boss")
        task = task_repo.find_task_by_id(task_id)
        assert task.column == "TODO"
        
        # Edit
        task_service.edit_task(task_id, {"description": "Updated"}, "Boss")
        task = task_repo.find_task_by_id(task_id)
        assert task.description == "Updated"
        
        # Move to DOING
        task_service.move_task(task_id, "DOING", "Boss")
        task = task_repo.find_task_by_id(task_id)
        assert task.column == "DOING"
        
        # Move to DONE
        task_service.move_task(task_id, "DONE", "Boss")
        task = task_repo.find_task_by_id(task_id)
        assert task.column == "DONE"
        
        # Delete
        result = task_service.delete_task(task_id, "Boss")
        assert result is True
        task = task_repo.find_task_by_id(task_id)
        assert task is None
