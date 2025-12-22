"""
Performance benchmark tests for CLI Kanban system.
Tests system performance under various load conditions.
"""
import pytest
import time
from services.auth_services import AuthService
from services.board_services import BoardService
from services.task_service import TaskService
from services.search_service import SearchService
from services.licence_service import LicenceService
from models.entities import Licence
from bson import ObjectId


class TestPerformanceBenchmarks:
    """Performance benchmarks for system operations."""
    
    def test_bulk_user_creation_performance(self, user_repo, licence_repo):
        """Benchmark creating multiple users."""
        # Arrange
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        num_users = 50
        
        # Create licences
        for i in range(num_users):
            licence = Licence(key=f"PERF-{i:04d}-{i:04d}-{i:04d}", owner_id=None, role="Members")
            licence_repo.create_licence(licence)
        
        # Act
        start_time = time.time()
        for i in range(num_users):
            auth_service.signup(
                username=f"user{i}",
                password="password123",
                email=f"user{i}@test.com",
                role="Members",
                licence_key=f"PERF-{i:04d}-{i:04d}-{i:04d}"
            )
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        avg_time_per_user = duration / num_users
        
        print(f"\nCreated {num_users} users in {duration:.3f}s")
        print(f"Average time per user: {avg_time_per_user:.4f}s")
        
        assert duration < 30.0, "User creation took too long"
        assert avg_time_per_user < 1.0, "Individual user creation too slow"
    
    def test_bulk_board_creation_performance(self, user_repo, board_repo, task_repo, licence_repo):
        """Benchmark creating multiple boards."""
        # Arrange
        licence = Licence(key="BOSS-PERF-1111-2222", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("perfboss", "pass", "boss@perf.com", "Boss", "BOSS-PERF-1111-2222")
        
        board_service = BoardService(board_repo, task_repo, user_repo)
        num_boards = 50
        
        # Act
        start_time = time.time()
        for i in range(num_boards):
            board_service.create_board(f"Board {i}", boss_id, "Boss")
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        avg_time_per_board = duration / num_boards
        
        print(f"\nCreated {num_boards} boards in {duration:.3f}s")
        print(f"Average time per board: {avg_time_per_board:.4f}s")
        
        assert duration < 20.0, "Board creation took too long"
        assert avg_time_per_board < 1.0, "Individual board creation too slow"
    
    def test_bulk_task_creation_performance(self, user_repo, board_repo, task_repo, licence_repo):
        """Benchmark creating many tasks on a single board."""
        # Arrange
        licence = Licence(key="BOSS-PERF-2222-3333", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("perfboss2", "pass", "boss2@perf.com", "Boss", "BOSS-PERF-2222-3333")
        
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Performance Board", boss_id, "Boss")
        
        task_service = TaskService(task_repo)
        num_tasks = 100
        
        # Act
        start_time = time.time()
        for i in range(num_tasks):
            column = ["TODO", "DOING", "DONE"][i % 3]
            priority = ["low", "medium", "high"][i % 3]
            task_service.create_task(
                title=f"Task {i}",
                board_id=board_id,
                column=column,
                user_role="Boss",
                description=f"Description for task {i}",
                priority=priority
            )
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        avg_time_per_task = duration / num_tasks
        
        print(f"\nCreated {num_tasks} tasks in {duration:.3f}s")
        print(f"Average time per task: {avg_time_per_task:.4f}s")
        
        assert duration < 30.0, "Task creation took too long"
        assert avg_time_per_task < 1.0, "Individual task creation too slow"
    
    def test_search_performance_large_dataset(self, user_repo, board_repo, task_repo, licence_repo):
        """Benchmark search performance with many tasks."""
        # Arrange
        licence = Licence(key="BOSS-PERF-3333-4444", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("perfboss3", "pass", "boss3@perf.com", "Boss", "BOSS-PERF-3333-4444")
        
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Search Perf Board", boss_id, "Boss")
        
        task_service = TaskService(task_repo)
        num_tasks = 100
        
        # Create tasks with various titles
        keywords = ["Implement", "Fix", "Update", "Refactor", "Test", "Deploy", "Review", "Design"]
        for i in range(num_tasks):
            keyword = keywords[i % len(keywords)]
            task_service.create_task(
                title=f"{keyword} feature {i}",
                board_id=board_id,
                column="TODO",
                user_role="Boss",
                description=f"Description with {keyword} keyword"
            )
        
        search_service = SearchService(task_repo)
        
        # Act - Search for each keyword
        search_times = []
        for keyword in keywords:
            start_time = time.time()
            results = search_service.search_tasks(board_id, keyword)
            end_time = time.time()
            search_times.append(end_time - start_time)
        
        # Assert
        avg_search_time = sum(search_times) / len(search_times)
        max_search_time = max(search_times)
        
        print(f"\nSearched {len(keywords)} keywords in {num_tasks} tasks")
        print(f"Average search time: {avg_search_time:.4f}s")
        print(f"Max search time: {max_search_time:.4f}s")
        
        assert avg_search_time < 1.0, "Average search time too slow"
        assert max_search_time < 2.0, "Max search time too slow"
    
    def test_task_movement_performance(self, user_repo, board_repo, task_repo, licence_repo):
        """Benchmark task movement between columns."""
        # Arrange
        licence = Licence(key="BOSS-PERF-5555-6666", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("perfboss5", "pass", "boss5@perf.com", "Boss", "BOSS-PERF-5555-6666")
        
        board_service = BoardService(board_repo, task_repo, user_repo)
        board_id = board_service.create_board("Move Perf Board", boss_id, "Boss")
        
        task_service = TaskService(task_repo)
        num_tasks = 50
        
        # Create tasks
        task_ids = []
        for i in range(num_tasks):
            task_id = task_service.create_task(f"Task {i}", board_id, "TODO", "Boss")
            task_ids.append(task_id)
        
        # Act - Move all tasks through workflow
        start_time = time.time()
        for task_id in task_ids:
            task_service.move_task(task_id, "DOING", "Boss")
            task_service.move_task(task_id, "DONE", "Boss")
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        total_moves = num_tasks * 2
        avg_time_per_move = duration / total_moves
        
        print(f"\nMoved {num_tasks} tasks through workflow ({total_moves} moves) in {duration:.3f}s")
        print(f"Average time per move: {avg_time_per_move:.4f}s")
        
        assert duration < 20.0, "Task movement took too long"
        assert avg_time_per_move < 1.0, "Individual task move too slow"

    def test_list_boards_performance_many_boards(self, user_repo, board_repo, task_repo, licence_repo):
        """Benchmark listing boards when many exist."""
        # Arrange
        licence = Licence(key="BOSS-LIST-1111-2222", owner_id=None, role="Boss")
        licence_repo.create_licence(licence)
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        boss_id, _ = auth_service.signup("listboss", "pass", "boss@list.com", "Boss", "BOSS-LIST-1111-2222")
        
        board_service = BoardService(board_repo, task_repo, user_repo)
        
        # Create many boards
        num_boards = 30
        for i in range(num_boards):
            board_service.create_board(f"List Board {i}", boss_id, "Boss")
        
        # Act
        start_time = time.time()
        boards = board_service.list_boards_for_user(boss_id, "Boss")
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        
        print(f"\nListed {len(boards)} boards in {duration:.3f}s")
        
        assert len(boards) == num_boards
        assert duration < 1.0, "Listing boards took too long"

    def test_login_performance(self, user_repo, licence_repo):
        """Benchmark login performance."""
        # Arrange
        licence = Licence(key="PERF-LOGI-1111-2222", owner_id=None, role="Members")
        licence_repo.create_licence(licence)
        
        auth_service = AuthService(user_repo=user_repo, licence_service=LicenceService(licence_repo))
        auth_service.signup("loginuser", "password123", "login@perf.com", "Members", "PERF-LOGI-1111-2222")
        
        # Act - Perform multiple logins
        num_logins = 20
        start_time = time.time()
        for _ in range(num_logins):
            user = auth_service.login("loginuser", "password123")
        end_time = time.time()
        
        # Assert
        duration = end_time - start_time
        avg_time_per_login = duration / num_logins
        
        print(f"\nPerformed {num_logins} logins in {duration:.3f}s")
        print(f"Average time per login: {avg_time_per_login:.4f}s")
        
        assert avg_time_per_login < 1.0, "Login time too slow"