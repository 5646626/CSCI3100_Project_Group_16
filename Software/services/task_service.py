from repositories.task_repository import TaskRepository
from models.entities import Task
from bson import ObjectId

#---------------Task Service-----------------#
class TaskService:
    
    def __init__(self, task_repo: TaskRepository = None):
        self.task_repo = task_repo or TaskRepository()
    
    def create_task(self, title: str, board_id: ObjectId, column: str,
                   user_role: str, description: str = None, due_date: str = None,
                   priority: str = "medium") -> ObjectId:
        # Hashira and Boss can create tasks, Members cannot.
        if user_role not in ["Hashira", "Boss"]:
            raise PermissionError(f"User role '{user_role}' cannot create tasks. Only 'Hashira' or 'Boss' can.")
        
        if priority not in ["high", "medium", "low"]:
            raise ValueError("Priority must be 'high', 'medium', or 'low'")
        
        task = Task(
            title=title,
            board_id=board_id,
            column=column,
            description=description,
            due_date=due_date,
            priority=priority
        )
        return self.task_repo.create_task(task)
    
    def get_task_by_id(self, task_id: ObjectId) -> Task:
        return self.task_repo.find_task_by_id(task_id)
    
    def list_tasks_in_column(self, board_id: ObjectId, column: str) -> list:
        return self.task_repo.find_task_by_column(board_id, column.upper())
    
    def edit_task(self, task_id: ObjectId, updates: dict, user_role: str) -> bool:
        if user_role not in ["Hashira", "Boss"]:
            raise PermissionError(f"User role '{user_role}' cannot edit tasks. Only 'Hashira' or 'Boss' can.")
        
        return self.task_repo.update_task(task_id, updates)
    
    def move_task(self, task_id: ObjectId, new_column: str, user_role: str) -> bool:
        if user_role not in ["Hashira", "Boss"]:
            raise PermissionError(f"User role '{user_role}' cannot move tasks. Only 'Hashira' or 'Boss' can.")
        
        valid_columns = ["TODO", "DOING", "DONE"]
        normalized_column = new_column.upper()
        if normalized_column not in valid_columns:
            raise ValueError(f"Invalid column. Must be one of {valid_columns}")

        return self.task_repo.update_task(task_id, {"column": normalized_column})
    
    def delete_task(self, task_id: ObjectId, user_role: str) -> bool:
        if user_role not in ["Hashira", "Boss"]:
            raise PermissionError(f"User role '{user_role}' cannot delete tasks. Only 'Hashira' or 'Boss' can.")
        
        return self.task_repo.delete_task(task_id)