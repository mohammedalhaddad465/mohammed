"""Database connection and queries with a reusable aiosqlite connection."""

from __future__ import annotations

import os
from typing import Any

import aiosqlite


DB_PATH = "database/archive.db"


class Database:
    """Encapsulates access to the SQLite database used by the bot.

    The class maintains a single connection that is reused across all calls. It
    also acts as an asynchronous context manager to ensure the connection is
    properly closed when the application finishes.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> aiosqlite.Connection:
        """Return a connection, creating it on first use."""

        if self._conn is None:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._conn = await aiosqlite.connect(self.db_path)
        return self._conn

    async def close(self) -> None:
        """Close the underlying connection if it exists."""

        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self) -> "Database":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()

    # ------------------------------------------------------------------
    # Schema initialisation
    # ------------------------------------------------------------------
    async def init_db(self) -> None:
        """Ensure database directory exists and run the schema file."""

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        db = await self.connect()
        with open("database/init.sql", "r", encoding="utf-8") as f:
            await db.executescript(f.read())
        await db.commit()

    # ------------------------------------------------------------------
    # Basic reads (levels / terms / subjects)
    # ------------------------------------------------------------------
    async def get_levels(self):
        db = await self.connect()
        cur = await db.execute("SELECT id, name FROM levels ORDER BY id")
        return await cur.fetchall()

    async def get_level_id_by_name(self, name: str) -> int | None:
        db = await self.connect()
        cur = await db.execute("SELECT id FROM levels WHERE name=?", (name,))
        row = await cur.fetchone()
        return row[0] if row else None

    async def get_term_id_by_name(self, name: str) -> int | None:
        db = await self.connect()
        cur = await db.execute("SELECT id FROM terms WHERE name=?", (name,))
        row = await cur.fetchone()
        return row[0] if row else None

    async def get_year_id_by_name(self, name: str) -> int | None:
        db = await self.connect()
        cur = await db.execute("SELECT id FROM years WHERE name=?", (name,))
        row = await cur.fetchone()
        return row[0] if row else None

    async def get_lecturer_id_by_name(self, name: str) -> int | None:
        db = await self.connect()
        cur = await db.execute("SELECT id FROM lecturers WHERE name=?", (name,))
        row = await cur.fetchone()
        return row[0] if row else None

    async def insert_level(self, name: str) -> None:
        db = await self.connect()
        await db.execute("INSERT OR IGNORE INTO levels (name) VALUES (?)", (name,))
        await db.commit()

    async def insert_term(self, name: str) -> None:
        db = await self.connect()
        await db.execute("INSERT OR IGNORE INTO terms (name) VALUES (?)", (name,))
        await db.commit()

    async def insert_subject(self, code: str, name: str, level_id: int, term_id: int) -> None:
        db = await self.connect()
        await db.execute(
            "INSERT INTO subjects (code, name, level_id, term_id) VALUES (?, ?, ?, ?)",
            (code, name, level_id, term_id),
        )
        await db.commit()

    async def insert_material(
        self,
        subject_id: int,
        section: str,
        category: str,
        title: str,
        url: str | None = None,
        year_id: int | None = None,
        lecturer_id: int | None = None,
    ) -> None:
        db = await self.connect()
        await db.execute(
            """
            INSERT INTO materials (subject_id, section, category, title, url, year_id, lecturer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (subject_id, section, category, title, url, year_id, lecturer_id),
        )
        await db.commit()

    async def insert_year(self, name: str) -> None:
        db = await self.connect()
        await db.execute("INSERT OR IGNORE INTO years (name) VALUES (?)", (name,))
        await db.commit()

    async def insert_lecturer(self, name: str, role: str = "lecturer") -> None:
        db = await self.connect()
        await db.execute(
            "INSERT OR IGNORE INTO lecturers (name, role) VALUES (?, ?)",
            (name, role),
        )
        await db.commit()

    async def ensure_year_id(self, name: str) -> int:
        _id = await self.get_year_id_by_name(name)
        if _id is not None:
            return _id
        await self.insert_year(name)
        _id = await self.get_year_id_by_name(name)
        if _id is None:
            raise RuntimeError(f"Failed to create year: {name}")
        return _id

    async def ensure_lecturer_id(self, name: str, role: str = "lecturer") -> int:
        _id = await self.get_lecturer_id_by_name(name)
        if _id is not None:
            return _id
        await self.insert_lecturer(name, role)
        _id = await self.get_lecturer_id_by_name(name)
        if _id is None:
            raise RuntimeError(f"Failed to create lecturer: {name}")
        return _id

    async def get_terms_by_level(self, level_id: int):
        """Return terms available for a given level."""

        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT t.id, t.name
            FROM terms t
            JOIN subjects s ON s.term_id = t.id
            WHERE s.level_id = ?
            ORDER BY t.id
            """,
            (level_id,),
        )
        return await cur.fetchall()

    async def get_subjects_by_level_and_term(self, level_id: int, term_id: int):
        """Return subject names for a given level and term."""

        db = await self.connect()
        cur = await db.execute(
            "SELECT name FROM subjects WHERE level_id = ? AND term_id = ? ORDER BY id",
            (level_id, term_id),
        )
        return await cur.fetchall()

    async def get_subject_id_by_name(self, level_id: int, term_id: int, subject_name: str) -> int | None:
        db = await self.connect()
        cur = await db.execute(
            "SELECT id FROM subjects WHERE level_id=? AND term_id=? AND name=?",
            (level_id, term_id, subject_name),
        )
        row = await cur.fetchone()
        return row[0] if row else None

    async def count_subjects(self, level_id: int, term_id: int) -> int:
        db = await self.connect()
        cur = await db.execute(
            "SELECT COUNT(*) FROM subjects WHERE level_id=? AND term_id=?",
            (level_id, term_id),
        )
        row = await cur.fetchone()
        return row[0] if row else 0

    async def term_feature_flags(self, level_id: int, term_id: int) -> dict:
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT section, COUNT(*) FROM materials m
            JOIN subjects s ON m.subject_id = s.id
            WHERE s.level_id=? AND s.term_id=?
            GROUP BY section
            """,
            (level_id, term_id),
        )
        rows = await cur.fetchall()
        return {section: count > 0 for section, count in rows}

    async def get_available_sections_for_subject(self, subject_id: int) -> list[str]:
        db = await self.connect()
        cur = await db.execute(
            "SELECT DISTINCT section FROM materials WHERE subject_id=? ORDER BY section",
            (subject_id,),
        )
        return [r[0] for r in await cur.fetchall()]

    async def get_years_for_subject_section(self, subject_id: int, section: str):
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT y.id, y.name
            FROM materials m
            JOIN years y ON m.year_id = y.id
            WHERE m.subject_id=? AND m.section=? AND m.year_id IS NOT NULL
            ORDER BY y.id
            """,
            (subject_id, section),
        )
        return await cur.fetchall()

    async def get_lecturers_for_subject_section(self, subject_id: int, section: str):
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT l.id, l.name
            FROM materials m
            JOIN lecturers l ON m.lecturer_id = l.id
            WHERE m.subject_id=? AND m.section=? AND m.lecturer_id IS NOT NULL
            ORDER BY l.id
            """,
            (subject_id, section),
        )
        return await cur.fetchall()

    async def has_lecture_category(self, subject_id: int, section: str) -> bool:
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT 1 FROM materials
            WHERE subject_id=? AND section=? AND category='lecture'
            LIMIT 1
            """,
            (subject_id, section),
        )
        return (await cur.fetchone()) is not None

    async def list_lecture_titles(self, subject_id: int, section: str) -> list[str]:
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT title FROM materials
            WHERE subject_id=? AND section=? AND title IS NOT NULL
            ORDER BY id
            """,
            (subject_id, section),
        )
        return [r[0] for r in await cur.fetchall()]

    async def list_lecture_titles_by_year(self, subject_id: int, section: str, year_id: int) -> list[str]:
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT title FROM materials
            WHERE subject_id=? AND section=? AND year_id=? AND title IS NOT NULL
            ORDER BY id
            """,
            (subject_id, section, year_id),
        )
        return [r[0] for r in await cur.fetchall()]

    async def list_lecture_titles_by_lecturer(self, subject_id: int, section: str, lecturer_id: int) -> list[str]:
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT title FROM materials
            WHERE subject_id=? AND section=? AND lecturer_id=? AND title IS NOT NULL
            ORDER BY id
            """,
            (subject_id, section, lecturer_id),
        )
        return [r[0] for r in await cur.fetchall()]

    async def list_lecture_titles_by_lecturer_year(
        self, subject_id: int, section: str, lecturer_id: int, year_id: int
    ) -> list[str]:
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT title FROM materials
            WHERE subject_id=? AND section=? AND lecturer_id=? AND year_id=? AND title IS NOT NULL
            ORDER BY id
            """,
            (subject_id, section, lecturer_id, year_id),
        )
        return [r[0] for r in await cur.fetchall()]

    async def get_years_for_subject_section_lecturer(
        self, subject_id: int, section: str, lecturer_id: int
    ):
        db = await self.connect()
        cur = await db.execute(
            """
            SELECT DISTINCT y.id, y.name
            FROM materials m
            JOIN years y ON m.year_id = y.id
            WHERE m.subject_id=? AND m.section=? AND m.lecturer_id=? AND m.year_id IS NOT NULL
            ORDER BY y.id
            """,
            (subject_id, section, lecturer_id),
        )
        return await cur.fetchall()

    async def get_lecture_materials(
        self,
        subject_id: int,
        section: str,
        *,
        year_id: int | None = None,
        lecturer_id: int | None = None,
        title: str | None = None,
    ):
        q = """
        SELECT id, category, title, url, year_id, lecturer_id
        FROM materials
        WHERE subject_id=? AND section=? AND category='lecture'
        """
        params: list[Any] = [subject_id, section]
        if year_id is not None:
            q += " AND year_id=?"
            params.append(year_id)
        if lecturer_id is not None:
            q += " AND lecturer_id=?"
            params.append(lecturer_id)
        if title is not None:
            q += " AND title=?"
            params.append(title)
        q += " ORDER BY id"

        db = await self.connect()
        cur = await db.execute(q, tuple(params))
        return await cur.fetchall()

    async def get_materials_by_category(
        self,
        subject_id: int,
        section: str,
        category: str,
        *,
        year_id: int | None = None,
        lecturer_id: int | None = None,
        title: str | None = None,
    ):
        q = """
        SELECT id, title, url
        FROM materials
        WHERE subject_id=? AND section=? AND category=?
        """
        params: list[Any] = [subject_id, section, category]
        if year_id is not None:
            q += " AND year_id=?"
            params.append(year_id)
        if lecturer_id is not None:
            q += " AND lecturer_id=?"
            params.append(lecturer_id)
        if title is not None:
            q += " AND title=?"
            params.append(title)
        q += " ORDER BY id"

        db = await self.connect()
        cur = await db.execute(q, tuple(params))
        return await cur.fetchall()

    async def list_categories_for_subject_section_year(
        self,
        subject_id: int,
        section: str,
        year_id: int,
        lecturer_id: int | None = None,
    ) -> list[str]:
        lecture_attachment_cats = (
            "slides",
            "audio",
            "board_images",
            "video",
            "mind_map",
            "transcript",
            "related",
        )
        placeholders = ",".join("?" * len(lecture_attachment_cats))
        q = f"""
        SELECT DISTINCT category
        FROM materials
        WHERE subject_id=? AND section=? AND year_id=? AND category IS NOT NULL
          AND category <> 'lecture'
          AND category NOT IN ({placeholders})
        """
        params: list[Any] = [subject_id, section, year_id, *lecture_attachment_cats]
        if lecturer_id is not None:
            q += " AND lecturer_id=?"
            params.append(lecturer_id)

        db = await self.connect()
        cur = await db.execute(q, tuple(params))
        return [r[0] for r in await cur.fetchall()]

    async def list_categories_for_lecture(
        self,
        subject_id: int,
        section: str,
        title: str,
        year_id: int | None = None,
        lecturer_id: int | None = None,
    ) -> list[str]:
        q = """
        SELECT DISTINCT category
        FROM materials
        WHERE subject_id=? AND section=? AND title=? AND category IS NOT NULL
        """
        params: list[Any] = [subject_id, section, title]
        if year_id is not None:
            q += " AND year_id=?"
            params.append(year_id)
        if lecturer_id is not None:
            q += " AND lecturer_id=?"
            params.append(lecturer_id)

        db = await self.connect()
        cur = await db.execute(q, tuple(params))
        return [r[0] for r in await cur.fetchall()]


__all__ = ["Database", "DB_PATH"]

