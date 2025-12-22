"""
Integration tests for CLI Kanban system.
Tests end-to-end workflows and interactions between services.
"""
import pytest
from services.auth_services import AuthService
from services.board_services import BoardService
from services.task_service import TaskService
from services.search_service import SearchService
from services.licence_service import LicenceService
from repositories.user_repository import UserRepository
from repositories.board_repository import BoardRepository
from repositories.task_repository import TaskRepository
from repositories.licence_repository import LicenceRepository
from models.entities import Licence
from bson import ObjectId


class TestIntegrationWorkflows:
    """Integration tests for complete user workflows."""
    
    def test_complete_user_signup_and_login_workflow(self, user_repo, licence_repo):
        """Test complete user registration and login flow."""
        # Arrange
        licence = Licence(key="INTG-1111-2222-3333", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        
        # Signup
        user_id, role = auth_service.signup(
            username="integrationuser",
            password="securepass123",
            email="integration@test.com",
            role="Members",
            licence_key="INTG-1111-2222-3333"
        )
        
        assert user_id is not None
        assert role == "Members"
        
        # Login
        logged_in_user = auth_service.login("integrationuser", "securepass123")
        assert logged_in_user is not None
        assert logged_in_user.username == "integrationuser"
        assert logged_in_user._id == user_id
        
        # Verify licence is claimed
        claimed_licence = licence_repo.find_licence_by_key("INTG-1111-2222-3333")
        assert claimed_licence.owner_id == user_id
    
    def test_boss_creates_board_and_manages_tasks(self, user_repo, board_repo, task_repo, licence_repo):
        """Test Boss creating board and managing tasks."""
        # Setup Boss user
        licence = Licence(key="BOSS-1111-2222-3333", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("boss", "pass123", "boss@test.com", "Boss", "BOSS-1111-2222-3333")
        
        # Create board
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Project Board", boss_id, "Boss")
        assert board_id is not None
        
        # Create tasks
        task_service = TaskService(task_repo)
        task1_id = task_service.create_task("Design UI", board_id, "TODO", "Boss", priority="high")
        task2_id = task_service.create_task("Implement API", board_id, "TODO", "Boss", priority="medium")
        
        # List tasks
        todo_tasks = task_service.list_tasks_in_column(board_id, "TODO")
        assert len(todo_tasks) == 2
        
        # Move task
        task_service.move_task(task1_id, "DOING", "Boss")
        doing_tasks = task_service.list_tasks_in_column(board_id, "DOING")
        assert len(doing_tasks) == 1
        
        # Complete task
        task_service.move_task(task2_id, "DONE", "Boss")
        done_tasks = task_service.list_tasks_in_column(board_id, "DONE")
        assert len(done_tasks) == 1
        
        # Verify TODO is empty
        todo_tasks = task_service.list_tasks_in_column(board_id, "TODO")
        assert len(todo_tasks) == 0
    
    def test_hashira_manages_tasks_on_boss_board(self, user_repo, board_repo, task_repo, licence_repo):
        """Test Hashira can manage tasks on Boss-created board."""
        # Setup Boss
        boss_licence = Licence(key="BOSS-2222-3333-4444", owner_id=None, role="Boss")
        licence_repo.create_licence(boss_licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("boss2", "pass123", "boss2@test.com", "Boss", "BOSS-2222-3333-4444")
        
        # Setup Hashira
        hashira_licence = Licence(key="HASH-2222-3333-4444", owner_id=None, role="Hashira")
        licence_repo.create_licence(hashira_licence)
        hashira_id, _ = auth_service.signup("hashira", "pass223", "hashira@test.com", "Hashira", "HASH-2222-3333-4444")
        
        # Boss creates board
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Team Board", boss_id, "Boss")
        
        # Hashira creates and manages tasks
        task_service = TaskService(task_repo)
        task_id = task_service.create_task("Fix bug", board_id, "TODO", "Hashira")
        
        # Hashira edits task
        task_service.edit_task(task_id, {"description": "Fixed critical bug"}, "Hashira")
        task = task_service.get_task_by_id(task_id)
        assert task.description == "Fixed critical bug"
        
        # Hashira moves task
        task_service.move_task(task_id, "DONE", "Hashira")
        task = task_service.get_task_by_id(task_id)
        assert task.column == "DONE"
    
    def test_member_views_boards_and_searches_tasks(self, user_repo, board_repo, task_repo, licence_repo):
        """Test Member can view boards and search tasks but cannot modify."""
        # Setup users
        boss_licence = Licence(key="BOSS-3333-4444-5555", owner_id=None, role="Boss")
        member_licence = Licence(key="MEMB-3333-4444-5555", owner_id=None, role="Members")
        licence_repo.create_licence(boss_licence)
        licence_repo.create_licence(member_licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("boss3", "pass123", "boss3@test.com", "Boss", "BOSS-3333-4444-5555")
        member_id, _ = auth_service.signup("member", "pass223", "member@test.com", "Members", "MEMB-3333-4444-5555")
        
        # Boss creates board and tasks
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Public Board", boss_id, "Boss")
        
        task_service = TaskService(task_repo)
        task_service.create_task("Important task", board_id, "TODO", "Boss", description="Critical issue")
        task_service.create_task("Regular task", board_id, "DOING", "Boss")
        
        # Member views boards
        boards = board_service.list_boards_for_user(member_id, "Members")
        assert len(boards) == 1
        
        # Member searches tasks
        search_service = SearchService(task_repo)
        search_results = search_service.search_tasks(board_id, "Important")
        assert len(search_results) == 1
        
        # Member cannot create tasks
        with pytest.raises(PermissionError):
            task_service.create_task("Unauthorized", board_id, "TODO", "Members")
    
    def test_board_deletion_cascades_to_tasks(self, user_repo, board_repo, task_repo, licence_repo):
        """Test deleting board also deletes all its tasks."""
        # Setup Boss
        licence = Licence(key="BOSS-4444-5555-6666", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("boss4", "pass123", "boss4@test.com", "Boss", "BOSS-4444-5555-6666")
        
        # Create board with tasks
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Temp Board", boss_id, "Boss")
        
        task_service = TaskService(task_repo)
        task1_id = task_service.create_task("Task 1", board_id, "TODO", "Boss")
        task2_id = task_service.create_task("Task 2", board_id, "DOING", "Boss")
        task3_id = task_service.create_task("Task 3", board_id, "DONE", "Boss")
        task_ids = [task1_id, task2_id, task3_id]
        
        # Verify tasks exist by ID
        existing_tasks = 0
        for task_id in task_ids:
            task = task_service.get_task_by_id(task_id)
            if task is not None:
                existing_tasks += 1
        assert existing_tasks == 3
        
        # Delete board
        board_service.delete_board("Temp Board", boss_id, "Boss")
        
        # Verify board is gone
        board = board_repo.find_board_by_id(board_id)
        assert board is None
        
        # Verify all task IDs are deleted
        existing_tasks_after = 0
        for task_id in task_ids:
            task = task_service.get_task_by_id(task_id)
            if task is not None:
                existing_tasks_after += 1
        assert existing_tasks_after == 0
    
    def test_multiple_users_different_roles(self, user_repo, board_repo, task_repo, licence_repo):
        """Test multiple users with different roles interacting."""
        # Setup licences and users
        licences = {
            "boss": Licence(key="BOSS-5555-6666-7777", owner_id=None, role="Boss"),
            "hashira1": Licence(key="HASH-5555-6666-7777", owner_id=None, role="Hashira"),
            "hashira2": Licence(key="HASH-5555-6666-8888", owner_id=None, role="Hashira"),
            "member": Licence(key="MEMB-5555-6666-7777", owner_id=None, role="Members")
        }
        for licence in licences.values():
            licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, boss_role = auth_service.signup("boss5", "pass123", "boss5@test.com", "Boss", "BOSS-5555-6666-7777")
        hashira1_id, hashira1_role = auth_service.signup("hashira1", "pass223", "h1@test.com", "Hashira", "HASH-5555-6666-7777")
        hashira2_id, hashira2_role = auth_service.signup("hashira2", "pass323", "h2@test.com", "Hashira", "HASH-5555-6666-8888")
        member_id, member_role = auth_service.signup("member2", "pass423", "m2@test.com", "Members", "MEMB-5555-6666-7777")
        
        # Boss creates board
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Team Project", boss_id, boss_role)
        
        # Hashira 1 creates task
        task_service = TaskService(task_repo)
        task1_id = task_service.create_task("Backend", board_id, "TODO", hashira1_role)
        
        # Hashira 2 creates task
        task2_id = task_service.create_task("Frontend", board_id, "TODO", hashira2_role)
        
        # Boss creates task
        task3_id = task_service.create_task("Documentation", board_id, "TODO", boss_role)
        
        # Verify all tasks exist
        all_tasks = task_service.list_tasks_in_column(board_id, "TODO")
        assert len(all_tasks) == 3
        
        # All users can view the board
        for user_id, role in [(boss_id, boss_role), (hashira1_id, hashira1_role), (member_id, member_role)]:
            boards = board_service.list_boards_for_user(user_id, role)
            assert len(boards) >= 1
    
    def test_task_search_and_filter_workflow(self, user_repo, board_repo, task_repo, licence_repo):
        """Test comprehensive search and filter workflow."""
        # Setup
        licence = Licence(key="BOSS-6666-7777-8888", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("boss6", "pass123", "boss6@test.com", "Boss", "BOSS-6666-7777-8888")
        
        # Create board with diverse tasks
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Search Test Board", boss_id, "Boss")
        
        task_service = TaskService(task_repo)
        task_service.create_task("Implement login", board_id, "TODO", "Boss", description="User authentication", priority="high")
        task_service.create_task("Implement signup", board_id, "TODO", "Boss", description="User registration", priority="high")
        task_service.create_task("Write tests", board_id, "DOING", "Boss", priority="medium")
        task_service.create_task("Fix bugs", board_id, "DONE", "Boss", priority="low")
        
        # Search by title keyword
        search_service = SearchService(task_repo)
        implement_tasks = search_service.search_tasks(board_id, "Implement")
        assert len(implement_tasks) == 2
        
        # Search by description
        user_tasks = search_service.search_tasks(board_id, "user")
        assert len(user_tasks) == 2
        user_task_titles = [task.title for task in user_tasks]
        assert "Implement login" in user_task_titles
        assert "Implement signup" in user_task_titles
    
    def test_permission_boundaries(self, user_repo, board_repo, task_repo, licence_repo):
        """Test permission boundaries between different roles."""
        # Setup all roles
        licences = {
            "boss": Licence(key="BOSS-7777-8888-9999", owner_id=None, role="Boss"),
            "hashira": Licence(key="HASH-7777-8888-9999", owner_id=None, role="Hashira"),
            "member": Licence(key="MEMB-7777-8888-9999", owner_id=None, role="Members")
        }
        for licence in licences.values():
            licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("boss7", "pass123", "boss7@test.com", "Boss", "BOSS-7777-8888-9999")
        hashira_id, _ = auth_service.signup("hashira7", "pass223", "h7@test.com", "Hashira", "HASH-7777-8888-9999")
        member_id, _ = auth_service.signup("member7", "pass323", "m7@test.com", "Members", "MEMB-7777-8888-9999")
        
        board_service = BoardService(board_repo, task_repo, user_repo)
        task_service = TaskService(task_repo)
        
        # Test board creation permissions
        board_id = board_service.create_board("Permission Test", boss_id, "Boss")
        
        with pytest.raises(PermissionError):
            board_service.create_board("Hashira Board", hashira_id, "Hashira")
        
        with pytest.raises(PermissionError):
            board_service.create_board("Member Board", member_id, "Members")
        
        # Test task creation permissions
        task_id = task_service.create_task("Boss Task", board_id, "TODO", "Boss")
        task_service.create_task("Hashira Task", board_id, "TODO", "Hashira")
        
        with pytest.raises(PermissionError):
            task_service.create_task("Member Task", board_id, "TODO", "Members")
        
        # Test task modification permissions
        task_service.edit_task(task_id, {"description": "Boss edit"}, "Boss")
        task_service.edit_task(task_id, {"description": "Hashira edit"}, "Hashira")
        
        with pytest.raises(PermissionError):
            task_service.edit_task(task_id, {"description": "Member edit"}, "Members")
        
        # Test board deletion permissions
        with pytest.raises(PermissionError):
            board_service.delete_board("Permission Test", hashira_id, "Hashira")
        
        with pytest.raises(PermissionError):
            board_service.delete_board("Permission Test", member_id, "Members")
        
        # Boss can delete
        result = board_service.delete_board("Permission Test", boss_id, "Boss")
        assert result is True
