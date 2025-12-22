from config import get_database
from pymongo import ASCENDING

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

# Licences: key, owner_id, role
licence_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["key", "role"],
        "properties": {
            "key": {"bsonType": "string", "minLength": 8},
            "owner_id": {"bsonType": ["objectId", "null"]},
            "role": {"enum": ["Members", "Hashira", "Boss"]},
        },
    }
}

# Tasks: title, board_id, column, description, due_date, priority, assigned_to
task_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "board_id", "column"],
        "properties": {
            "title": {"bsonType": "string", "minLength": 1},
            "board_id": {"bsonType": "objectId"},
            "column": {"enum": ["TODO", "DOING", "DONE"]},
            "description": {"bsonType": ["string", "null"]},
            "due_date": {"bsonType": ["string", "null"], "pattern": r"^\d{4}-\d{2}-\d{2}$"},
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

# -----------------Schema Setup Logic-----------------#
# Create collection with validator or update its validator if it exists
def _ensure_collection(db, name: str, validator: dict):
    try:
        db.create_collection(name, validator=validator)
    except Exception as e:
        if "already exists" in str(e):
            db.command({"collMod": name, "validator": validator, "validationLevel": "strict", "validationAction": "error"})
        else:
            raise

# Ensure all collections exist with proper validators and indexes.
def ensure_schema():
    db = get_database()

    # Apply validators
    _ensure_collection(db, "users", user_schema)
    _ensure_collection(db, "boards", board_schema)
    _ensure_collection(db, "tasks", task_schema)
    _ensure_collection(db, "licences", licence_schema)

    # Helpful indexes
    # Uniqueness (handle existing non-unique indexes gracefully)
    def _ensure_unique_index(coll, field: str, name: str):
        try:
            # Inspect existing indexes
            for idx in coll.list_indexes():
                key_spec = idx.get("key")
                # key_spec is an ordered dict like {field: 1}
                if key_spec == {field: 1}:
                    if idx.get("unique", False):
                        # Already unique; nothing to do
                        return
                    # Drop the conflicting non-unique index before creating the unique one
                    coll.drop_index(idx["name"])
                    break
            # Create the desired unique index with a stable name
            coll.create_index([(field, ASCENDING)], name=name, unique=True)
        except Exception as e:
            # Surface a clear warning but do not fail schema setup entirely
            print(f"Warning: Failed to ensure unique index on {coll.name}.{field}: {e}")

    _ensure_unique_index(db["users"], "username", name="username_unique")
    _ensure_unique_index(db["users"], "email", name="email_unique")
    _ensure_unique_index(db["licences"], "key", name="licence_key_unique")
    db["boards"].create_index("owner_id")
    db["boards"].create_index("name")
    db["tasks"].create_index("board_id")
    db["tasks"].create_index("assigned_to")
    db["tasks"].create_index("priority")
    db["licences"].create_index("owner_id")


if __name__ == "__main__":
    ensure_schema()