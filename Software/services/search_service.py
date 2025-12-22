from repositories.task_repository import TaskRepository
from bson import ObjectId

#---------------Search Service-----------------#
class SearchService:
    
    def __init__(self, task_repo: TaskRepository = None):
        self.task_repo = task_repo or TaskRepository()
    
    # Search tasks by keyword in title or description
    def search_tasks(self, board_id: ObjectId, keyword: str) -> list:
        return self.task_repo.search_task(board_id, keyword)

#----------Not currenly used, but could implemented in the future----------#
#   Filter tasks by column (status) and assignee
#    def filter_tasks(self, board_id: ObjectId, status: str = None, 
#                    assignee_id: ObjectId = None) -> list:
#        all_tasks = self.task_repo.find_task_by_board(board_id)
#
#        filtered = all_tasks
#       if status:
#            normalized_status = status.upper()
#            filtered = [t for t in filtered if t.column == normalized_status]
#        if assignee_id:
#            filtered = [t for t in filtered if t.assigned_to == assignee_id]
#        
#        return filtered