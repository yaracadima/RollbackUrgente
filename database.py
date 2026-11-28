"""MongoDB connection helpers."""

import os
from functools import lru_cache

from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()
@lru_cache(maxsize=1)
def get_database():
    """Return the configured MongoDB database, creating the client lazily."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("Define MONGODB_URI para conectar con MongoDB.")
    print(os.getenv("MONGODB_URI"))
    print(os.getenv("MONGODB_DATABASE"))
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    database_name = os.getenv("MONGODB_DATABASE", "cineplus")
    return client[database_name]


def get_movies_collection():
    return get_database()["movies"]


def dbConnection():
    """Compatibility helper used by the existing Flask routes."""
    return get_database()

