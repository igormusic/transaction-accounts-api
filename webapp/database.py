"""Database module."""

from contextlib import contextmanager, AbstractContextManager
from datetime import datetime
from typing import Callable
import logging

from sqlalchemy import create_engine, orm, Column, DateTime
from sqlalchemy.orm import Session, DeclarativeBase

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Database:

    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
