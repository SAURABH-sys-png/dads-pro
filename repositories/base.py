"""
Base repository helpers shared by all concrete repositories.
"""

from __future__ import annotations

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from models.entities import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Thin generic CRUD helpers; domain repos add query methods."""

    def __init__(self, session: Session, model: Type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: int) -> Optional[ModelT]:
        return self.session.get(self.model, entity_id)

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()
