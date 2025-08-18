from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Subject:
    """Represents a study subject."""
    id: int
    name: str


@dataclass
class Lecturer:
    """Represents a lecturer or teaching assistant."""
    id: int
    name: str
    role: str = "lecturer"


@dataclass
class Material:
    """Represents a material record from the database."""
    id: int
    subject_id: int
    section: str
    category: str
    title: str
    url: Optional[str] = None
    year_id: Optional[int] = None
    lecturer_id: Optional[int] = None
