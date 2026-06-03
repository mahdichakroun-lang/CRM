"""
Generic base repository providing common CRUD operations.
All domain repositories inherit from this.
"""
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from app.shared.base_model import BaseEntity

ModelType = TypeVar("ModelType", bound=BaseEntity)


class BaseRepository(Generic[ModelType]):
    """Generic repository with CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        query = self.db.query(self.model)

        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, str):
                        query = query.filter(column.ilike(f"%{value}%"))
                    else:
                        query = query.filter(column == value)

        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        else:
            query = query.order_by(self.model.id.desc())

        return query.offset(skip).limit(limit).all()

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = self.db.query(self.model)
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, str):
                        query = query.filter(column.ilike(f"%{value}%"))
                    else:
                        query = query.filter(column == value)
        return query.count()

    def create(self, data: Dict[str, Any]) -> ModelType:
        entity = self.model(**data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True

    def exists(self, entity_id: int) -> bool:
        return self.db.query(
            self.db.query(self.model).filter(self.model.id == entity_id).exists()
        ).scalar()
