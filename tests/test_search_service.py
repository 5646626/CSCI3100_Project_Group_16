"""
Tests for SearchService.
Tests task searching functionality.
"""
import pytest
from services.search_service import SearchService
from repositories.task_repository import TaskRepository
from models.entities import Task
from bson import ObjectId


class TestSearchService:
    """Test suite for search functionality."""
    
    def test_search_tasks_by_title(self, task_repo, sample_board):
        """Test searching tasks by keyword in title."""
        # Arrange
        search_service = SearchService(task_repo=task_repo)
        task1 = Task(title="Implement feature", board_id=sample_board._id, column="TODO")
        task2 = Task(title="Write tests", board_id=sample_board._id, column="DOING")
        task3 = Task(title="Implement bug fix", board_id=sample_board._id, column="DONE")
        task_repo.create_task(task1)
        task_repo.create_task(task2)
        task_repo.create_task(task3)
        
        # Act
        results = search_service.search_tasks(sample_board._id, "Implement")
        
        # Assert
        assert len(results) == 2
        titles = [t.title for t in results]
        assert "Implement feature" in titles
        assert "Implement bug fix" in titles
    
    def test_search_tasks_by_description(self, task_repo, sample_board):
        """Test searching tasks by keyword in description."""
        # Arrange
        search_service = SearchService(task_repo=task_repo)
        task1 = Task(title="Task 1", board_id=sample_board._id, column="TODO", description="Fix database connection")
        task2 = Task(title="Task 2", board_id=sample_board._id, column="DOING", description="Update UI")
        task3 = Task(title="Task 3", board_id=sample_board._id, column="DONE", description="Fix login bug")
        task_repo.create_task(task1)
        task_repo.create_task(task2)
        task_repo.create_task(task3)
        
        # Act
        results = search_service.search_tasks(sample_board._id, "Fix")
        
        # Assert
        assert len(results) == 2
        descriptions = [t.description for t in results]
        assert "Fix database connection" in descriptions
        assert "Fix login bug" in descriptions
    
    def test_search_tasks_case_insensitive(self, task_repo, sample_board):
        """Test search is case-insensitive."""
        # Arrange
        search_service = SearchService(task_repo=task_repo)
        task = Task(title="Important Task", board_id=sample_board._id, column="TODO")
        task_repo.create_task(task)
        
        # Act
        results_lower = search_service.search_tasks(sample_board._id, "important")
        results_upper = search_service.search_tasks(sample_board._id, "IMPORTANT")
        results_mixed = search_service.search_tasks(sample_board._id, "ImPoRtAnT")
        
        # Assert
        assert len(results_lower) == 1
        assert len(results_upper) == 1
        assert len(results_mixed) == 1
    
    def test_search_tasks_no_results(self, task_repo, sample_board):
        """Test searching with no matching results."""
        # Arrange
        search_service = SearchService(task_repo=task_repo)
        task = Task(title="Example Task", board_id=sample_board._id, column="TODO")
        task_repo.create_task(task)
        
        # Act
        results = search_service.search_tasks(sample_board._id, "nonexistent")
        
        # Assert
        assert len(results) == 0
    
    def test_search_tasks_partial_match(self, task_repo, sample_board):
        """Test searching with partial keyword match."""
        # Arrange
        search_service = SearchService(task_repo=task_repo)
        task = Task(title="Testing functionality", board_id=sample_board._id, column="TODO")
        task_repo.create_task(task)
        
        # Act
        results = search_service.search_tasks(sample_board._id, "Test")
        
        # Assert
        assert len(results) == 1
    
    def test_search_empty_board(self, task_repo, sample_board):
        """Test searching on empty board."""
        # Arrange
        search_service = SearchService(task_repo=task_repo)
        
        # Act
        results = search_service.search_tasks(sample_board._id, "anything")
        
        # Assert
        assert len(results) == 0
    
