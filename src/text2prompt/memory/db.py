"""SQLite database operations for prompt history."""

import os
import sqlite3


class Database:
    """SQLite database connection wrapper."""

    def __init__(self, path: str):
        self.path = path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize database and create tables.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLite connection object
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def get_history(conn: sqlite3.Connection, context_id: str) -> list[tuple[str, str]]:
    """Get chat history for a context.

    Args:
        conn: SQLite connection
        context_id: Context identifier

    Returns:
        List of (role, content) tuples, limited to last 10 entries
    """
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM chat_history WHERE context_id = ? ORDER BY id ASC LIMIT 10",
        (context_id,),
    )
    return c.fetchall()


def save_interaction(
    conn: sqlite3.Connection,
    context_id: str,
    user_text: str,
    assistant_text: str,
) -> None:
    """Save a user-assistant interaction.

    Args:
        conn: SQLite connection
        context_id: Context identifier
        user_text: User's input text
        assistant_text: Assistant's response
    """
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (context_id, role, content) VALUES (?, ?, ?)",
        (context_id, "user", user_text),
    )
    c.execute(
        "INSERT INTO chat_history (context_id, role, content) VALUES (?, ?, ?)",
        (context_id, "assistant", assistant_text),
    )
    conn.commit()

    # Trim old history, keep last 10 entries
    c.execute(
        """
        DELETE FROM chat_history
        WHERE id NOT IN (
            SELECT id FROM chat_history
            WHERE context_id = ?
            ORDER BY id DESC LIMIT 10
        ) AND context_id = ?
    """,
        (context_id, context_id),
    )
    conn.commit()


def clear_memory(conn: sqlite3.Connection, context_id: str) -> None:
    """Clear all history for a context.

    Args:
        conn: SQLite connection
        context_id: Context identifier
    """
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE context_id = ?", (context_id,))
    conn.commit()
