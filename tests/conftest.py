"""
Pytest configuration and shared fixtures for CLI Kanban tests.
"""
import pytest
import os
from pymongo import MongoClient
from bson import ObjectId

# Test database configuration
TEST_DATABASE_NAME = "cli-kanban-test"
# Ensure product code uses the test database via environment variable BEFORE importing Software
os.environ["DATABASE_NAME"] = TEST_DATABASE_NAME

# Import product modules after setting test env
from repositories.mongodb_adapter import MongoDBAdapter
from repositories.user_repository import UserRepository
from repositories.board_repository import BoardRepository
from repositories.task_repository import TaskRepository
from repositories.licence_repository import LicenceRepository
from models.base_user import Members, Hashira, Boss
from models.entities import Board, Task, Licence

@pytest.fixture(scope="function")
def test_db():
    """Provide a clean test database for each test."""
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client[TEST_DATABASE_NAME]
    
    # Clean up before test
    for collection_name in db.list_collection_names():
        db[collection_name].drop()
    
    yield db
    
    # Clean up after test
    for collection_name in db.list_collection_names():
        db[collection_name].drop()
    
    client.close()

@pytest.fixture(scope="function")
def adapter(test_db):
    """Provide a MongoDB adapter connected to test database."""
    return MongoDBAdapter()

@pytest.fixture
def user_repo(adapter):
    """Provide a clean UserRepository instance."""
    return UserRepository(adapter=adapter)

@pytest.fixture
def board_repo(adapter):
    """Provide a clean BoardRepository instance."""
    return BoardRepository(adapter=adapter)

@pytest.fixture
def task_repo(adapter):
    """Provide a clean TaskRepository instance."""
    return TaskRepository(adapter=adapter)

@pytest.fixture
def licence_repo(adapter):
    """Provide a clean LicenceRepository instance."""
    return LicenceRepository(adapter=adapter)

@pytest.fixture
def sample_member_user(user_repo):
    """Create and return a sample Members user."""
    user = Members(
        username="testmember",
        password_hash=UserRepository.hash_password("password123"),
        email="member@test.com",
        role="Members"
    )
    user_id = user_repo.create_new_user(user)
    user._id = user_id
    return user

@pytest.fixture
def sample_hashira_user(user_repo):
    """Create and return a sample Hashira user."""
    user = Hashira(
        username="testhashira",
        password_hash=UserRepository.hash_password("password123"),
        email="hashira@test.com"
    )
    user_id = user_repo.create_new_user(user)
    user._id = user_id
    return user

@pytest.fixture
def sample_boss_user(user_repo):
    """Create and return a sample Boss user."""
    user = Boss(
        username="testboss",
        password_hash=UserRepository.hash_password("password123"),
        email="boss@test.com"
    )
    user_id = user_repo.create_new_user(user)
    user._id = user_id
    return user

@pytest.fixture
def sample_board(board_repo, sample_boss_user):
    """Create and return a sample board."""
    board = Board(name="Test Board", owner_id=sample_boss_user._id)
    board_id = board_repo.create_board(board)
    board._id = board_id
    return board

@pytest.fixture
def sample_task(task_repo, sample_board):
    """Create and return a sample task."""
    task = Task(
        title="Test Task",
        board_id=sample_board._id,
        column="TODO",
        description="Test description",
        priority="medium"
    )
    task_id = task_repo.create_task(task)
    task._id = task_id
    return task

@pytest.fixture
def sample_licence(licence_repo):
    """Create and return a sample unclaimed licence."""
    licence = Licence(
        key="TEST-1234-ABCD-5678",
        owner_id=None,
        role="Members"
    )
    licence_id = licence_repo.create_licence(licence)
    licence._id = licence_id
    return licence

@pytest.fixture
def sample_licences_all_roles(licence_repo):
    """Create and return licences for all roles."""
    licences = {
        "Members": Licence(key="MEMB-1111-2222-3333", owner_id=None, role="Members"),
        "Hashira": Licence(key="HASH-4444-5555-6666", owner_id=None, role="Hashira"),
        "Boss": Licence(key="BOSS-7777-8888-9999", owner_id=None, role="Boss")
    }
    
    for role, licence in licences.items():
        licence_id = licence_repo.create_licence(licence)
        licence._id = licence_id
    
    return licences
