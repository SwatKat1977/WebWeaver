import os
import sqlite3
import logging
import threading
from typing import Any, Optional
from webweaver.weavegate.service_state import ServiceState


class SqliteInterfaceException(Exception):
    """Exception for SQLite interaction errors."""


class SqliteInterface:
    """
    Thread-safe SQLite interface with consistent connection configuration and
    predictable behaviour.
    """

    __slots__ = ["_db_filename", "_lock", "_logger", "_state_manager"]

    SQLITE_HEADER = b"SQLite format 3\x00"

    def __init__(self,
                 logger: logging.Logger,
                 db_filename: str,
                 state_manager: ServiceState) -> None:
        self._db_filename: str = db_filename
        self._lock = threading.RLock()
        self._logger = logger.getChild(__name__)
        self._state_manager = state_manager

    #
    # ──────────────────────────────────────────────────────────────
    # Validation
    # ──────────────────────────────────────────────────────────────
    #

    def is_valid_database(self) -> bool:
        try:
            with open(self._db_filename, "rb") as file:
                return file.read(len(self.SQLITE_HEADER)) == self.SQLITE_HEADER
        except (OSError, FileNotFoundError):
            return False

    def ensure_valid(self) -> None:
        if not os.path.exists(self._db_filename):
            raise SqliteInterfaceException("Database file does not exist")

        if not self.is_valid_database():
            raise SqliteInterfaceException("Database file format is not valid")

    #
    # ──────────────────────────────────────────────────────────────
    # Connection handling
    # ──────────────────────────────────────────────────────────────
    #

    def _get_connection(self, validate: bool = True) -> sqlite3.Connection:
        """
        Create a new configured SQLite connection.

        Applies:
        - WAL journal mode (better concurrency)
        - foreign key enforcement
        - busy timeout (avoids immediate lock failures)
        """

        if validate:
            self.ensure_valid()

        conn = sqlite3.connect(
            self._db_filename,
            timeout=5.0,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # Configure connection (IMPORTANT)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")

        return conn

    #
    # ──────────────────────────────────────────────────────────────
    # Core operations
    # ──────────────────────────────────────────────────────────────
    #

    def create_table(self, schema: str, table_name: str) -> None:
        with self._lock:
            try:
                with self._get_connection(validate=False) as conn:
                    conn.execute(schema)
            except sqlite3.Error as ex:
                raise SqliteInterfaceException(
                    f"Create table failure for {table_name}: {ex}"
                ) from ex

    def run_query(self,
                  query: str,
                  params: tuple = (),
                  fetch_one: bool = False,
                  commit: bool = False) -> Any:
        """
        Execute a SQL query.

        Returns:
            - commit=True → affected row count (int)
            - fetch_one=True → tuple or ()
            - SELECT → list of rows
            - otherwise → None
        """

        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute(query, params)

                    if commit:
                        conn.commit()
                        return cursor.rowcount

                    if fetch_one:
                        row = cursor.fetchone()
                        return row if row is not None else ()

                    if cursor.description:
                        return cursor.fetchall()

                    return None

            except sqlite3.Error as ex:
                raise SqliteInterfaceException(f"Query error: {ex}") from ex

    def insert_query(self,
                     query: str,
                     params: tuple = ()) -> Optional[int]:
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute(query, params)
                    conn.commit()
                    return cursor.lastrowid

            except sqlite3.Error as ex:
                raise SqliteInterfaceException(
                    f"Insert query failed: {ex}"
                ) from ex

    def bulk_insert_query(self, query: str, value_sets: list[tuple]) -> bool:
        with self._lock:
            try:
                with self._get_connection() as conn:
                    conn.executemany(query, value_sets)
                    conn.commit()
                    return True

            except sqlite3.Error as ex:
                raise SqliteInterfaceException(
                    f"Bulk insert query failed: {ex}"
                ) from ex

    def delete_query(self, query: str, params: tuple = ()) -> None:
        with self._lock:
            try:
                with self._get_connection() as conn:
                    conn.execute(query, params)
                    conn.commit()

            except sqlite3.Error as ex:
                raise SqliteInterfaceException(
                    f"Delete query failed: {ex}"
                ) from ex

    def _handle_db_error(self, error_message: str, ex: Exception,
                         log_level: int = logging.CRITICAL) -> None:
        """Centralized error handling and state update."""
        self._logger.log(log_level, "%s, reason: %s", error_message, str(ex))
        self._state_manager.mark_database_failed(str(ex))

    def safe_query(self,
                   query: str,
                   values: tuple = (),
                   error_message: str = "",
                   log_level: int = logging.CRITICAL,
                   fetch_one: bool = False,
                   commit: bool = False) -> Optional[Any]:
        """Safely execute a database query with maintenance-mode enforcement."""
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        if not self._state_manager.is_operational():
            raise RuntimeError(
                "Service in maintenance mode; refusing database operation.")

        try:
            return self.run_query(query,
                                  values,
                                  fetch_one=fetch_one,
                                  commit=commit)

        except (sqlite3.Error, SqliteInterfaceException) as ex:
            self._handle_db_error(error_message, ex, log_level)
            return None

    def safe_insert_query(self,
                          query: str,
                          values: tuple,
                          error_message: str,
                          log_level: int = logging.CRITICAL) -> Optional[int]:
        """Safely execute an INSERT query and return last inserted row ID."""
        if not self._state_manager.is_operational():
            raise RuntimeError(
                "Service in maintenance mode; refusing database operation.")

        try:
            with self._lock, self._get_connection() as conn:
                cursor = conn.execute(query, values)
                conn.commit()
                return cursor.lastrowid

        except sqlite3.Error as ex:
            self._handle_db_error(error_message, ex, log_level)
            return None

    def safe_bulk_insert(self,
                         query: str,
                         value_sets: list[tuple],
                         error_message: str,
                         log_level: int = logging.CRITICAL) -> bool:
        """
        Safely execute a bulk insert operation with maintenance-mode support.
        """
        if not self._state_manager.is_operational():
            raise RuntimeError(
                "Service in maintenance mode; refusing database operation.")

        try:
            return self.bulk_insert_query(query, value_sets)

        except sqlite3.Error as ex:
            self._handle_db_error(error_message, ex, log_level)
            return False
