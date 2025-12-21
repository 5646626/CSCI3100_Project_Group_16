import os
from pymongo import MongoClient

#-----------------Configuration settings------------------#
# Get MongoDB connection settings from environment variables or use defaults
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "cli-kanban")

# Get or create a singleton MongoClient instance
def get_mongo_client():
    return MongoClient(MONGO_URI)

# Get the CLI-Kanban database instance
def get_database():
    client = get_mongo_client()
    return client[DATABASE_NAME]