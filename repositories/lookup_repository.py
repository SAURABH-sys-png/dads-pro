"""
Lookup repositories for categories and units (combo-box data).
"""

from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.dto import LookupDTO
from models.entities import Category, Unit
from repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Category)

    def list_active(self) -> List[LookupDTO]:
        rows = self.session.scalars(
            select(Category).where(Category.is_active.is_(True)).order_by(Category.name.asc())
        ).all()
        return [LookupDTO(id=r.id, name=r.name) for r in rows]


class UnitRepository(BaseRepository[Unit]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Unit)

    def list_active(self) -> List[LookupDTO]:
        rows = self.session.scalars(
            select(Unit).where(Unit.is_active.is_(True)).order_by(Unit.name.asc())
        ).all()
        return [LookupDTO(id=r.id, name=r.name) for r in rows]
