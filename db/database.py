"""
SelfMaster - Database Layer (SQLAlchemy)
Ініціалізація рушія, сесії та схеми.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from config import (
    APP_DIR, DATABASE_URL, DB_ECHO_SQL,
    SEED_HABITS, SEED_CRITERIA,
)
from .models import Base, Habit, IdealCriterion


# ═══════════════════════════════════════════════════════════════
# ENGINE
# ═══════════════════════════════════════════════════════════════

def _make_engine():
    APP_DIR.mkdir(parents=True, exist_ok=True)

    is_sqlite = DATABASE_URL.startswith("sqlite")
    kwargs: dict = {"echo": DB_ECHO_SQL}

    if is_sqlite:
        # StaticPool + check_same_thread=False для однопотокового десктопного застосунку
        kwargs.update(
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    engine = create_engine(DATABASE_URL, **kwargs)

    # Вмикаємо foreign keys + WAL для SQLite при кожному з'єднанні
    if is_sqlite:
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, _connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.close()

    return engine


engine = _make_engine()

# ═══════════════════════════════════════════════════════════════
# SESSION FACTORY
# ═══════════════════════════════════════════════════════════════

SessionFactory = sessionmaker(bind=engine, autoflush=True, autocommit=False)


@contextmanager
def get_session() -> Session:
    """
    Контекстний менеджер сесії.

    Використання:
        with get_session() as s:
            habits = s.query(Habit).all()
    """
    session: Session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# INIT / SEED
# ═══════════════════════════════════════════════════════════════

def init_db() -> None:
    """Створює всі таблиці та заповнює початковими даними."""
    Base.metadata.create_all(engine)
    _seed_defaults()


def _seed_defaults() -> None:
    """Додає дефолтні звички та критерії, якщо таблиці порожні."""
    with get_session() as s:
        if not s.query(Habit).first():
            for data in SEED_HABITS:
                s.add(Habit(**data))

        if not s.query(IdealCriterion).first():
            for data in SEED_CRITERIA:
                s.add(IdealCriterion(**data))


def drop_all() -> None:
    """УВАГА: видаляє всі таблиці (тільки для тестів)."""
    Base.metadata.drop_all(engine)