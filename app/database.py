"""
app/database.py – SQLite data-access layer.
"""

from __future__ import annotations
import sqlite3
import datetime
import os


class Database:

    DB_FILE = "data/pomodoro.db"

    def __init__(self) -> None:
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(self.DB_FILE)
        self.cursor = self.conn.cursor()
        self.today = str(datetime.date.today())
        self._migrate()

    # ── Schema ────────────────────────────────
    def _migrate(self) -> None:
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                status     TEXT    NOT NULL DEFAULT 'pending',
                date_added TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ledger (
                date          TEXT PRIMARY KEY,
                study_minutes INTEGER NOT NULL DEFAULT 0
            );
            -- New: each goal type holds multiple line items
            CREATE TABLE IF NOT EXISTS goal_items (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type  TEXT    NOT NULL,
                content    TEXT    NOT NULL,
                position   INTEGER NOT NULL DEFAULT 0
            );
        """
        )

        # Roll-over pending tasks to today
        self.cursor.execute(
            "UPDATE tasks SET date_added = ? "
            "WHERE status = 'pending' AND date_added != ?",
            (self.today, self.today),
        )
        # Ensure today's ledger row
        self.cursor.execute(
            "INSERT OR IGNORE INTO ledger (date, study_minutes) VALUES (?, 0)",
            (self.today,),
        )
        self.conn.commit()

    # ── Ledger ────────────────────────────────
    def get_study_minutes(self, date: str | None = None) -> int:
        date = date or self.today
        self.cursor.execute("SELECT study_minutes FROM ledger WHERE date = ?", (date,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def add_study_minutes(self, minutes: int, date: str | None = None) -> None:
        date = date or self.today
        self.cursor.execute(
            "UPDATE ledger SET study_minutes = study_minutes + ? WHERE date = ?",
            (minutes, date),
        )
        self.conn.commit()

    def get_ledger_for_date(self, date: str) -> dict | None:
        self.cursor.execute("SELECT study_minutes FROM ledger WHERE date = ?", (date,))
        row = self.cursor.fetchone()
        return {"date": date, "study_minutes": row[0]} if row else None

    # ── Tasks ─────────────────────────────────
    def get_tasks(self, date: str | None = None) -> list[tuple]:
        date = date or self.today
        self.cursor.execute(
            "SELECT id, name, status FROM tasks WHERE date_added = ?", (date,)
        )
        return self.cursor.fetchall()

    def add_task(self, name: str) -> None:
        self.cursor.execute(
            "INSERT INTO tasks (name, status, date_added) VALUES (?, 'pending', ?)",
            (name, self.today),
        )
        self.conn.commit()

    def complete_task(self, task_id: int) -> None:
        self.cursor.execute(
            "UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,)
        )
        self.conn.commit()

    def count_tasks(self, date: str | None = None) -> tuple[int, int]:
        date = date or self.today
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE date_added = ?", (date,))
        total = self.cursor.fetchone()[0]
        self.cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE date_added = ? AND status = 'completed'",
            (date,),
        )
        done = self.cursor.fetchone()[0]
        return total, done

    def get_tasks_for_date(self, date: str) -> list[tuple]:
        self.cursor.execute(
            "SELECT name, status FROM tasks WHERE date_added = ?", (date,)
        )
        return self.cursor.fetchall()

    # ── Goal Items (CRUD) ─────────────────────
    def get_goal_items(self, goal_type: str) -> list[tuple[int, str]]:
        """Returns [(id, content), …] ordered by position."""
        self.cursor.execute(
            "SELECT id, content FROM goal_items "
            "WHERE goal_type = ? ORDER BY position ASC, id ASC",
            (goal_type,),
        )
        return self.cursor.fetchall()

    def add_goal_item(self, goal_type: str, content: str) -> int:
        """Insert a new item at the end. Returns new row id."""
        self.cursor.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM goal_items WHERE goal_type = ?",
            (goal_type,),
        )
        pos = self.cursor.fetchone()[0]
        self.cursor.execute(
            "INSERT INTO goal_items (goal_type, content, position) VALUES (?, ?, ?)",
            (goal_type, content, pos),
        )
        self.conn.commit()
        return self.cursor.lastrowid  # type: ignore[return-value]

    def update_goal_item(self, item_id: int, content: str) -> None:
        self.cursor.execute(
            "UPDATE goal_items SET content = ? WHERE id = ?",
            (content, item_id),
        )
        self.conn.commit()

    def delete_goal_item(self, item_id: int) -> None:
        self.cursor.execute("DELETE FROM goal_items WHERE id = ?", (item_id,))
        self.conn.commit()

    # ── Cleanup ───────────────────────────────
    def close(self) -> None:
        self.conn.close()
