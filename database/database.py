import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / ".odie" / "odie.db"


class DatabaseManager:
    """Handles SQLite database connection and schema initialization."""

    _instance = None  # Singleton instance

    def __new__(cls, db_path=DB_PATH):
        """Ensures only one instance of DatabaseManager is created."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_db(db_path)
        return cls._instance

    def _init_db(self, db_path):
        """Initializes the database connection and ensures schema exists."""
        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self):
        """Ensures the database exists and initializes tables."""
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign keys
            self.create_tables(conn)

    def get_connection(self):
        """Returns a new SQLite database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")  # Ensure FK enforcement
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self, conn):
        """Creates necessary tables if they do not exist."""
        with conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    old_root TEXT NOT NULL,
                    new_root TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    migration_id INTEGER NOT NULL,
                    FOREIGN KEY (migration_id) REFERENCES migrations(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    migration_id INTEGER NOT NULL,
                    FOREIGN KEY (migration_id) REFERENCES migrations(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    site_id INTEGER NOT NULL,
                    client_id INTEGER NOT NULL,
                    migration_id INTEGER NOT NULL,
                    FOREIGN KEY (site_id) REFERENCES sites(id),
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (migration_id) REFERENCES migrations(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    project_id INTEGER NOT NULL,
                    flagged INTEGER DEFAULT 0,
                    migration_id INTEGER NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (migration_id) REFERENCES migrations(id) ON DELETE CASCADE
                );
            """)


class BaseDAO:
    """Stateless Base Data Access Object providing reusable database methods."""

    _table = None  # Subclasses must define this
    _pk = "id"  # Default primary key column name
    _columns = set()
    _requires_migration = True  # Disable for migrations

    @staticmethod
    def get_connection():
        """Returns a new database connection."""
        return DatabaseManager().get_connection()

    @classmethod
    def _initialize_columns(cls):
        """
        Retrieves the column names for the table dynamically from the database schema.
        This method runs once per DAO to prevent repeated queries.
        """
        if not cls._columns:  # Only fetch once
            with cls.get_connection() as conn:
                query = f"PRAGMA table_info({cls._table})"
                result = conn.execute(query).fetchall()
                cls._columns = {row[1] for row in result}  # Column names are in index 1


    @classmethod
    def validate_columns(cls, kwargs):
        """
        Ensures all keys in `kwargs` match valid columns for the table.
        Raises a ValueError if an invalid column is detected.

        :param kwargs:
        """
        cls._initialize_columns()

        invalid_keys = set(kwargs.keys()) - cls._columns
        if invalid_keys:
            raise ValueError(f"Invalid column(s) for {cls._table}: {', '.join(invalid_keys)}")

    @classmethod
    def add(cls, **kwargs):
        """
        Inserts a new row into the table dynamically.

        This method constructs an `INSERT INTO` statement dynamically based on `kwargs`,
        where the keys represent the column names, and the values are the corresponding
        values to be inserted.

        If `_requires_migration` is `True`, the method automatically injects the
        active `migration_id` before executing the query.

        Args:
            **kwargs: Dictionary where keys represent column names and values represent
                      the data to be inserted.

        Raises:
            ValueError: If `_requires_migration` is `True` but no active migration is found.

        Example Usage:
            - Insert a project:
                ProjectDAO.add(name="New Project", site_id=2, client_id=3)

            - Insert a client:
                ClientDAO.add(name="Big Company")

            - Insert a migration (does NOT require `migration_id`):
                MigrationDAO.add(name="Initial Migration", old_root="/old/path", new_root="/new/path")
        """
        cls.validate_columns(kwargs)

        if cls._requires_migration:
            migration_id = MigrationDAO.get_active_migration_id()
            if migration_id is None:
                raise ValueError("No active migration found! Cannot insert without a migration_id.")
            kwargs["migration_id"] = migration_id  # Auto-add migration_id

        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        values = tuple(kwargs.values())

        query = f"INSERT INTO {cls._table} ({columns}) VALUES ({placeholders})"

        with cls.get_connection() as conn:
            conn.execute(query, values)

    @classmethod
    def get_all(cls):
        """Retrieves all rows from the table."""
        query = f"SELECT * FROM {cls._table}"

        with cls.get_connection() as conn:
            return conn.execute(query).fetchall()

    @classmethod
    def update(cls, _id, **kwargs):
        """
        Updates an existing row by primary key (`id`), modifying only the specified fields.

        This method constructs an `UPDATE` statement dynamically based on `kwargs`, where
        the keys represent the column names to update, and the values are the corresponding
        new values.

        Args:
            _id (int): The primary key of the record to update.
            **kwargs: Dictionary where keys represent column names and values represent
                      the new data to update.

        Example Usage:
            - Update a project's name:
                ProjectDAO.update(3, name="Updated Project Name")

            - Mark a file as flagged:
                FileDAO.update(5, flagged=1)

        Raises:
            ValueError: If `kwargs` is empty, preventing an invalid SQL statement.

        Notes:
            - This method does NOT allow changing the primary key (`id`).
            - Only fields specified in `kwargs` are updated.
        """
        cls.validate_columns(kwargs)

        set_clause = ", ".join(f"{key} = ?" for key in kwargs.keys())
        values = tuple(kwargs.values()) + (_id,)

        query = f"UPDATE {cls._table} SET {set_clause} WHERE {cls._pk} = ?"

        with cls.get_connection() as conn:
            conn.execute(query, values)

    @classmethod
    def delete(cls, _id):
        """Deletes a row by primary key."""
        query = f"DELETE FROM {cls._table} WHERE {cls._pk} = ?"

        with cls.get_connection() as conn:
            conn.execute(query, (_id,))

class MigrationDAO(BaseDAO):
    """Stateless Data Access Object for the migrations table."""

    _table = "migrations"
    _requires_migration = False  # No migration_id needed for migrations

    @classmethod
    def set_active_migration(cls, migration_id):
        """Marks a migration as active and ensures all others are inactive."""
        with cls.get_connection() as conn:
            conn.execute("UPDATE migrations SET is_active = 0")  # Deactivate all
            conn.execute("UPDATE migrations SET is_active = 1 WHERE id = ?", (migration_id,))

    @classmethod
    def get_active_migration_id(cls):
        """Returns the ID of the active migration, or None if none exist."""
        with cls.get_connection() as conn:
            result = conn.execute("SELECT id FROM migrations WHERE is_active = 1").fetchone()
            return result[0] if result else None

class ClientDAO(BaseDAO):
    """Data Access Object for the clients table."""
    _table = "clients"

class ProjectDAO(BaseDAO):
    """Data Access Object for the projects table."""
    _table = "projects"

class FileDAO(BaseDAO):
    """Data Access Object for the files table."""
    _table = "files"

class SiteDAO(BaseDAO):
    """Data Access Object for the sites table."""
    _table = "sites"