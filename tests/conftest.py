# conftest.py
import sqlite3
import pytest
from unittest.mock import patch
from database import DatabaseManager

@pytest.fixture(scope="session")
def in_memory_db():
    # Create an in-memory SQLite connection
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON;")
    # Set up database schema and seed data
    with connection as conn:
        conn.executescript("""
            CREATE TABLE migrations (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                old_root TEXT NOT NULL,
                new_root TEXT NOT NULL,
                is_active INTEGER DEFAULT 0
            );
            
            INSERT INTO migrations (name, old_root, new_root, is_active) 
            VALUES ('Test Migration', 'old/root', 'new/root', 1);
        """)
    # Patch DatabaseManager.get_connection to always use the in-memory database
    patcher = patch.object(DatabaseManager, "get_connection", return_value=connection)
    patcher.start()
    yield connection  # Provide the connection to tests
    # Cleanup: stop the patch and close the connection
    patcher.stop()
    connection.close()