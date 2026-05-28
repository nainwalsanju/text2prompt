"""SQLite database operations for prompt history."""

import os
import sqlite3
import threading

# Module-level lock to serialize all database access.
# Although ``check_same_thread=False`` disables Python's thread-ownership
# check, SQLite itself is not safe for truly concurrent writes.
_db_lock = threading.Lock()


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize database and create tables.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLite connection object
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    with _db_lock:
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
    with _db_lock:
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
    with _db_lock:
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
    with _db_lock:
        c = conn.cursor()
        c.execute("DELETE FROM chat_history WHERE context_id = ?", (context_id,))
        conn.commit()

