from __future__ import annotations
from bson import ObjectId

# ----------------Entity Classes-----------------#
class Board:
    def __init__(self, name: str, owner_id: ObjectId, columns: list[str] | None = None, _id: ObjectId = None):
        self._id = _id
        self.name = name
        self.owner_id = owner_id
        # All boards have the classic board with TODO, DOING, DONE columns by default
        # Can be extended to a customised board in the future
        self.columns = columns or ["TODO", "DOING", "DONE"]

    def to_dict(self):
        result = {
            "name": self.name,
            "owner_id": self.owner_id,
            "columns": self.columns,
        }
        if self._id is not None:    # Check if _id exists, if yes then include it
            result["_id"] = self._id
        return result

class Task:
    def __init__(
        self,
        title: str,
        board_id: ObjectId,
        column: str,
        description: str | None = None,
        due_date: str | None = None,
        priority: str = "medium",   # default is set to medium
        assigned_to: ObjectId | None = None,    #The functionality of assign tasks is not implemented
        _id: ObjectId = None,
    ):
        self._id = _id
        self.title = title
        self.board_id = board_id
        # Force classic columns (TODO, DOING, DONE), customised columns are not implemented yet
        valid_columns = {"TODO", "DOING", "DONE"}
        normalized_column = column.upper()
        if normalized_column not in valid_columns:
            raise ValueError(f"Invalid column: {column}. Must be one of {sorted(valid_columns)}.")
        self.column = normalized_column
        self.description = description
        self.due_date = due_date
        self.priority = priority
        # Can be extended to assign tasks to users in the future
        self.assigned_to = assigned_to

    def to_dict(self):
        result = {
            "title": self.title,
            "board_id": self.board_id,
            "column": self.column,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
        }
        if self._id is not None:
            result["_id"] = self._id
        return result


class Licence:
    def __init__(self, key: str, owner_id: ObjectId | None = None, role: str = "Members", _id: ObjectId = None):
        self._id = _id
        self.key = key
        self.owner_id = owner_id
        self.role = role

    def to_dict(self):
        result = {
            "key": self.key,
            "owner_id": self.owner_id,
            "role": self.role,
        }
        if self._id is not None:    # Check if _id exists, if yes then include it
            result["_id"] = self._id
        return result