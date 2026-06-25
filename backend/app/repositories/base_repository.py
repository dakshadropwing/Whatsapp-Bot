"""Base Repository class."""
from __future__ import annotations

from typing import Any, Generic, Type, TypeVar, Optional, List
from sqlalchemy import select
from app.extensions import db

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Generic Base Repository wrapping basic database operations.
    All specialist repositories inherit from this class.
    """
    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def get(self, id: Any) -> Optional[T]:
        """Fetch a record by primary key."""
        return db.session.get(self.model, id)

    def get_all(self) -> List[T]:
        """Fetch all records."""
        return db.session.execute(select(self.model)).scalars().all()

    def create(self, **kwargs: Any) -> T:
        """Create and add a new record to the session."""
        instance = self.model(**kwargs)
        db.session.add(instance)
        return instance

    def update(self, instance: T, **kwargs: Any) -> T:
        """Update fields on an existing record."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

    def delete(self, instance: T) -> None:
        """Delete a record."""
        db.session.delete(instance)

    def save(self) -> None:
        """Commit current transaction changes to the database."""
        db.session.commit()
