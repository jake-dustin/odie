# test_dao.py
import pytest
from database import BaseDAO

class TestDAO(BaseDAO):
    """Mock DAO for testing BaseDAO functionality."""
    _table = "test_table"
    _pk = "id"

@pytest.fixture(scope="module")
def setup_test_table(in_memory_db):
    """Creates the test_table for tests in this module."""
    with in_memory_db as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                email TEXT,
                migration_id INTEGER,
                FOREIGN KEY (migration_id) REFERENCES migrations (id)
            );
        """)
    yield
    # Optional cleanup: drop the test_table after tests run
    with in_memory_db as conn:
        conn.execute("DROP TABLE IF EXISTS test_table")

@pytest.fixture(autouse=True)
def clear_test_table(setup_test_table, in_memory_db):
    """Clears test_table before each test that uses it."""
    TestDAO._columns = None
    with in_memory_db as conn:
        conn.execute("DELETE FROM test_table")
    yield

def test_validate_columns_valid(in_memory_db):
    try:
        TestDAO.validate_columns({"name": "John Doe", "age": 30, "email": "test@example.com"})
    except ValueError:
        pytest.fail("validate_columns() raised ValueError unexpectedly!")

def test_validate_columns_invalid(in_memory_db):
    with pytest.raises(ValueError) as exc_info:
        TestDAO.validate_columns({"name": "Alice", "invalid_column": "test"})
    assert "invalid_column" in str(exc_info.value)

def test_add_valid_data(in_memory_db):
    TestDAO.add(name="John Doe", age=30, email="john@example.com")
    results = TestDAO.get_all()
    assert len(results) == 1
    assert results[0][1] == "John Doe"

def test_add_invalid_data(in_memory_db):
    with pytest.raises(ValueError):
        TestDAO.add(name="John Doe", invalid_column="error")

def test_get_all(in_memory_db):
    TestDAO.add(name="Alice", age=25, email="alice@example.com")
    TestDAO.add(name="Bob", age=40, email="bob@example.com")
    results = TestDAO.get_all()
    assert len(results) == 2

def test_update_existing_record(in_memory_db):
    TestDAO.add(name="Charlie", age=22, email="charlie@example.com")
    record = TestDAO.get_all()[0]
    record_id = record[0]
    TestDAO.update(record_id, name="Charlie Updated", age=23)
    updated_record = TestDAO.get_all()[0]
    assert updated_record[1] == "Charlie Updated"
    assert updated_record[2] == 23

def test_update_invalid_column(in_memory_db):
    TestDAO.add(name="David", age=28, email="david@example.com")
    record = TestDAO.get_all()[0]
    record_id = record[0]
    with pytest.raises(ValueError):
        TestDAO.update(record_id, invalid_column="error")

def test_delete_existing_record(in_memory_db):
    TestDAO.add(name="Eve", age=32, email="eve@example.com")
    record = TestDAO.get_all()[0]
    record_id = record[0]
    TestDAO.delete(record_id)
    results = TestDAO.get_all()
    assert len(results) == 0

def test_delete_non_existing_record(in_memory_db):
    try:
        TestDAO.delete(9999)
    except Exception as e:
        pytest.fail(f"delete() raised an unexpected exception: {e}")