"""
Database engine and session factory.

Uses SQLite with foreign keys enabled. The database file sits next to
the executable (or project root) so a USB copy is self-contained.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from models.entities import Base
from utils.logger import get_logger
from utils.paths import get_database_path

logger = get_logger("database")

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def _sqlite_url() -> str:
    db_path = get_database_path()
    # Absolute path required for reliable USB / frozen deployments
    return f"sqlite:///{db_path.as_posix()}"


def _enable_foreign_keys(dbapi_conn, connection_record) -> None:  # noqa: ANN001
    """SQLite disables FK checks by default — turn them on per connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine(echo: bool = False) -> Engine:
    """Create (once) and return the shared SQLAlchemy engine."""
    global _engine, _SessionLocal
    if _engine is None:
        url = _sqlite_url()
        logger.info("Opening SQLite database: %s", url)
        _engine = create_engine(
            url,
            echo=echo,
            future=True,
            connect_args={"check_same_thread": False},
        )
        event.listen(_engine, "connect", _enable_foreign_keys)
        _SessionLocal = sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return the configured session factory (initializes engine if needed)."""
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Commits on success, rolls back on exception, always closes the session.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables() -> None:
    """Create all ORM tables if they do not already exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    # Ensure WAL-friendly pragmas for desktop multi-reader safety
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.commit()
    logger.info("Database schema ensured at %s", get_database_path())


def reset_engine() -> None:
    """Dispose engine (used after restore so the new file is reopened)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
