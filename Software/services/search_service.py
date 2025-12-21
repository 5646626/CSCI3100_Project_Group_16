from repositories.task_repository import TaskRepository
from bson import ObjectId

class SearchService:
    """Service for searching and filtering tasks (all roles can access)."""
    
    def __init__(self, task_repo: TaskRepository = None):
        self.task_repo = task_repo or TaskRepository()
    
    def search_tasks(self, board_id: ObjectId, keyword: str) -> list:
        """Search tasks by keyword in title or description."""
        return self.task_repo.search(board_id, keyword)
    
    def filter_tasks(self, board_id: ObjectId, status: str = None, 
                    assignee_id: ObjectId = None) -> list:
        """Filter tasks by column (status) and assignee."""
        all_tasks = self.task_repo.find_by_board(board_id)

        filtered = all_tasks
        if status:
            normalized_status = status.upper()
            filtered = [t for t in filtered if t.column == normalized_status]
        if assignee_id:
            filtered = [t for t in filtered if t.assigned_to == assignee_id]
        
        return filtered