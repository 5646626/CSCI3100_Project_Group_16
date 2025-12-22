from config import get_database

#-----------------Schema and Models-----------------#
# Align schemas to actual entity fields

# Users: username, password_hash, email, role
user_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "email", "password_hash", "role"],
        "properties": {
            "username": {"bsonType": "string", "minLength": 1},
            "email": {"bsonType": "string", "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$"},
            "password_hash": {"bsonType": "string"},
            "role": {"enum": ["Members", "Hashira", "Boss"]},
        },
    }
}

# Tasks: title, board_id, column, description?, due_date?, priority, assigned_to?
task_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "board_id", "column"],
        "properties": {
            "title": {"bsonType": "string", "minLength": 1},
            "board_id": {"bsonType": "objectId"},
            "column": {"enum": ["TODO", "DOING", "DONE"]},
            "description": {"bsonType": ["string", "null"]},
            "due_date": {"bsonType": ["string", "null"]},
            "priority": {"enum": ["low", "medium", "high"]},
            "assigned_to": {"bsonType": ["objectId", "null"]},
        },
    }
}

# Boards: name, owner_id, columns
board_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "owner_id", "columns"],
        "properties": {
            "name": {"bsonType": "string", "minLength": 1},
            "owner_id": {"bsonType": "objectId"},
            "columns": {
                "bsonType": "array",
                "items": {"enum": ["TODO", "DOING", "DONE"]},
            },
        },
    }
}


def _ensure_collection(db, name: str, validator: dict):
    """Create collection with validator or update its validator if it exists."""
    try:
        db.create_collection(name, validator=validator)
    except Exception as e:
        if "already exists" in str(e):
            db.command({"collMod": name, "validator": validator, "validationLevel": "strict", "validationAction": "error"})
        else:
            raise


def ensure_schema():
    """Ensure all collections exist with proper validators and indexes."""
    db = get_database()

    # Apply validators
    _ensure_collection(db, "users", user_schema)
    _ensure_collection(db, "boards", board_schema)
    _ensure_collection(db, "tasks", task_schema)

    # Helpful indexes
    # Uniqueness
    db["users"].create_index("username", unique=True)
    db["users"].create_index("email", unique=True)
    db["boards"].create_index("owner_id")
    db["boards"].create_index("name")
    db["tasks"].create_index("board_id")
    db["tasks"].create_index("assigned_to")
    db["tasks"].create_index("priority")


if __name__ == "__main__":
    ensure_schema()