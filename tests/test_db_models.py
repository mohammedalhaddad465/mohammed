import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.db import Database
from bot.models import Subject, Lecturer, Material
from bot.keyboards import generate_subjects_keyboard, generate_lecturers_keyboard


def test_db_returns_dataclasses(tmp_path):
    async def inner():
        db_file = tmp_path / "test.db"
        db = Database(str(db_file))
        async with db:
            await db.init_db()
            await db.insert_level("Level1")
            await db.insert_term("Term1")
            level_id = await db.get_level_id_by_name("Level1")
            term_id = await db.get_term_id_by_name("Term1")
            await db.insert_subject("S1", "Subject1", level_id, term_id)
            subjects = await db.get_subjects_by_level_and_term(level_id, term_id)
            assert subjects and isinstance(subjects[0], Subject)
            subject_id = subjects[0].id
            lect_id = await db.ensure_lecturer_id("Dr X")
            await db.insert_material(subject_id, "theory", "lecture", "Intro", "http://url", lecturer_id=lect_id)
            lecturers = await db.get_lecturers_for_subject_section(subject_id, "theory")
            assert lecturers and isinstance(lecturers[0], Lecturer)
            mats = await db.get_lecture_materials(subject_id, "theory")
            assert mats and isinstance(mats[0], Material)

    asyncio.run(inner())


def test_keyboards_accept_dataclasses():
    subjects = [Subject(id=1, name="Math"), Subject(id=2, name="Physics")]
    kb = generate_subjects_keyboard(subjects)
    kb_dict = kb.to_dict()
    texts = [btn["text"] for row in kb_dict["keyboard"] for btn in row]
    assert "Math" in texts and "Physics" in texts

    lecturers = [Lecturer(id=1, name="Prof")]
    kb2 = generate_lecturers_keyboard(lecturers)
    kb2_dict = kb2.to_dict()
    texts2 = [btn["text"] for row in kb2_dict["keyboard"] for btn in row]
    assert "Prof" in texts2
