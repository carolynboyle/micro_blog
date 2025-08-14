"""
db_utils.py
-----------
Reusable database helpers for SQLite.
Safe for use with Flask or other frameworks.
"""

from __future__ import annotations
import sqlite3 as sq
from typing import Any, List, Optional, Tuple

def create_database_connection(database_name: str) -> Optional[sq.Connection]:
    """Create a new SQLite database connection."""
    try:
        conn = sq.connect(database_name)
        conn.row_factory = sq.Row  # Access columns by name
        return conn
    except sq.Error as e:
        # Use logging instead of print to integrate with Flask
        import logging
        logging.error(f"Error creating database connection: {e}")
        return None

def safe_close_connection(connection: Optional[sq.Connection]) -> None:
    """Safely close a database connection."""
    if connection:
        try:
            connection.close()
        except sq.Error as e:
            import logging
            logging.warning(f"Error closing database connection: {e}")

def execute_query(
    connection: sq.Connection,
    query: str,
    params: Optional[tuple] = None,
    fetch_type: str = "none"
) -> Any:
    """
    Execute an SQL query safely with error handling.
    fetch_type: 'none', 'one', or 'all'
    """
    try:
        with connection:  # handles commit/rollback automatically
            cur = connection.cursor()
            cur.execute(query, params or ())
            if fetch_type == "one":
                return cur.fetchone()
            elif fetch_type == "all":
                return cur.fetchall() or []
            else:
                return cur.rowcount
    except sq.Error as e:
        import logging
        logging.error(f"Database error: {e} | Query: {query}")
        return None

def table_exists(connection: sq.Connection, table_name: str) -> bool:
    """Return True if the specified table exists."""
    result = execute_query(
        connection,
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,),
        fetch_type="one"
    )
    return result is not None

def database_is_ready(connection: Optional[sq.Connection], table_name: str) -> bool:
    """
    Check if a database connection exists and contains a table.
    UI should handle messaging if False is returned.
    """
    if connection is None:
        return False
    return table_exists(connection, table_name)

def get_all_records(connection: sq.Connection, table_name: str, order_by: str | None = None) -> List[sq.Row]:
    """Return all rows from a table, optionally ordered."""
    query = f"SELECT * FROM {table_name}"
    if order_by:
        # Sanitize: whitelist columns if using user input
        query += f" ORDER BY {order_by}"
    return execute_query(connection, query, fetch_type="all") or []

def get_record_by_id(connection: sq.Connection, table_name: str, id_column: str, record_id: Any) -> Optional[sq.Row]:
    """Return a single row by ID."""
    query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
    return execute_query(connection, query, (record_id,), fetch_type="one")

def get_column_values(connection: sq.Connection, table_name: str, column_name: str, order_by: str | None = None) -> List[Any]:
    """Return all values from one column."""
    query = f"SELECT {column_name} FROM {table_name}"
    if order_by:
        query += f" ORDER BY {order_by}"
    rows = execute_query(connection, query, fetch_type="all") or []
    return [row[0] for row in rows]

def record_exists(connection: sq.Connection, table_name: str, id_column: str, record_id: Any) -> bool:
    """Return True if a record with this ID exists."""
    query = f"SELECT 1 FROM {table_name} WHERE {id_column} = ? LIMIT 1"
    result = execute_query(connection, query, (record_id,), fetch_type="one")
    return result is not None
