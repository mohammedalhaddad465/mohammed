"""
Script to seed database from YAML file.
"""

import asyncio
from pathlib import Path

import yaml
from bot.db import Database

# Database instance
_db = Database()

# ---------------- Helper utilities ----------------

ALLOWED_TABLES = {"levels", "terms"}

async def _get_id_by_name(table: str, name: str) -> int | None:
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")
    conn = await _db.connect()
    cur = await conn.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = await cur.fetchone()
    return row[0] if row else None

async def ensure_level_id(name: str) -> int:
    _id = await _get_id_by_name("levels", name)
    if _id is not None:
        return _id
    await _db.insert_level(name)
    _id = await _get_id_by_name("levels", name)
    if _id is None:
        raise RuntimeError(f"Failed to create level: {name}")
    return _id

async def ensure_term_id(name: str) -> int:
    _id = await _get_id_by_name("terms", name)
    if _id is not None:
        return _id
    await _db.insert_term(name)
    _id = await _get_id_by_name("terms", name)
    if _id is None:
        raise RuntimeError(f"Failed to create term: {name}")
    return _id

async def add_subjects(level_name: str, term_name: str, pairs: list[tuple[str, str]]):
    """Add subjects for a level/term."""
    level_id = await ensure_level_id(level_name)
    term_id = await ensure_term_id(term_name)
    for code, name in pairs:
        if code.strip() == "---":
            continue
        await _db.insert_subject(code, name, level_id, term_id)

async def _subject_id(level_name: str, term_name: str, subject_name: str) -> int:
    level_id = await _db.get_level_id_by_name(level_name)
    term_id = await _db.get_term_id_by_name(term_name)
    if not (level_id and term_id):
        raise RuntimeError(f"Level/Term not found: {level_name} / {term_name}")
    sid = await _db.get_subject_id_by_name(level_id, term_id, subject_name)
    if not sid:
        raise RuntimeError(f"Subject not found: {subject_name} ({level_name}/{term_name})")
    return sid

# ---------------- YAML loading ----------------

def _load_data() -> dict:
    path = Path(__file__).with_name("seed_data.yml")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------------- Seeding helpers ----------------

async def seed_structure(structure: dict):
    for level in structure.get("levels", []):
        level_name = level["name"]
        for term in level.get("terms", []):
            term_name = term["name"]
            pairs = [(s["code"], s["name"]) for s in term.get("subjects", [])]
            await add_subjects(level_name, term_name, pairs)
    print("✅ تم إدخال الهيكل (مستويات/أترام/مواد).")

async def seed_years_and_lecturers(data: dict):
    years = {key: await _db.ensure_year_id(val) for key, val in data.get("years", {}).items()}
    people = {
        key: await _db.ensure_lecturer_id(info["name"], info["role"])
        for key, info in data.get("lecturers", {}).items()
    }
    return {"years": years, "people": people}

async def seed_materials_variants(data: dict, ctx: dict):
    Y = ctx["years"]; P = ctx["people"]
    for entry in data.get("materials", []):
        sid = await _subject_id(entry["level"], entry["term"], entry["subject"])
        for item in entry.get("items", []):
            await _db.insert_material(
                sid,
                item["section"],
                item["kind"],
                item["title"],
                item.get("url"),
                Y[item["year"]],
                P.get(item.get("person"))
            )

# ---------------- Entry point ----------------

async def main():
    data = _load_data()
    async with _db:
        await seed_structure(data["structure"])
        ctx = await seed_years_and_lecturers(data)
        await seed_materials_variants(data, ctx)
        print("🎉 اكتمل إدخال البيانات (شغّله مرة واحدة فقط).")

if __name__ == "__main__":
    asyncio.run(main())
