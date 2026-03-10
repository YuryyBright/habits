"""
SelfMaster - ORM моделі (SQLAlchemy)
Визначення таблиць через декларативний стиль.
"""
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, event,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ═══════════════════════════════════════════════════════════════
# HABIT
# ═══════════════════════════════════════════════════════════════

class Habit(Base):
    """Звичка — шаблон, що відстежується щодня."""
    __tablename__ = "habits"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str]           = mapped_column(String(120), nullable=False)
    emoji:       Mapped[str]           = mapped_column(String(10),  default="⭐")
    type:        Mapped[str]           = mapped_column(String(20),  default="toggle")  # toggle | number
    unit:        Mapped[Optional[str]] = mapped_column(String(30))
    category:    Mapped[str]           = mapped_column(String(40),  default="general")
    goal_value:  Mapped[Optional[float]] = mapped_column(Float)
    is_negative: Mapped[bool]          = mapped_column(Boolean, default=False)
    color:       Mapped[str]           = mapped_column(String(10),  default="#c8f135")
    sort_order:  Mapped[int]           = mapped_column(Integer, default=0)
    is_active:   Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at:  Mapped[date]          = mapped_column(Date, default=date.today)

    # Відносини
    logs: Mapped[List["HabitLog"]] = relationship(
        "HabitLog", back_populates="habit",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name={self.name!r} type={self.type}>"

    def is_done_value(self, value: Optional[str]) -> bool:
        """Перевіряє чи значення вважається 'виконаним' для цієї звички."""
        if value is None:
            return False
        if value == "done":
            return True
        if value == "fail":
            return False
        try:
            n = float(value)
            return n == 0 if self.is_negative else n > 0
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "name":        self.name,
            "emoji":       self.emoji,
            "type":        self.type,
            "unit":        self.unit,
            "category":    self.category,
            "goal_value":  self.goal_value,
            "is_negative": self.is_negative,
            "color":       self.color,
            "sort_order":  self.sort_order,
            "is_active":   self.is_active,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════
# HABIT LOG
# ═══════════════════════════════════════════════════════════════

class HabitLog(Base):
    """Денний запис виконання звички."""
    __tablename__ = "habit_logs"
    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_log"),
    )

    id:         Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    habit_id:   Mapped[int]           = mapped_column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    log_date:   Mapped[date]          = mapped_column(Date, nullable=False)
    value:      Mapped[Optional[str]] = mapped_column(String(50))   # 'done' | 'fail' | '15.5'
    note:       Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    # Відносини
    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")

    def __repr__(self) -> str:
        return f"<HabitLog habit_id={self.habit_id} date={self.log_date} value={self.value!r}>"

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "habit_id": self.habit_id,
            "log_date": self.log_date.isoformat(),
            "value":    self.value,
            "note":     self.note,
        }


# ═══════════════════════════════════════════════════════════════
# IDEAL CRITERION
# ═══════════════════════════════════════════════════════════════

class IdealCriterion(Base):
    """Критерій ідеальної людини."""
    __tablename__ = "ideal_criteria"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    category:    Mapped[str]           = mapped_column(String(40), nullable=False)
    title:       Mapped[str]           = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon:        Mapped[str]           = mapped_column(String(10),  default="🎯")
    sort_order:  Mapped[int]           = mapped_column(Integer, default=0)
    is_active:   Mapped[bool]          = mapped_column(Boolean, default=True)

    # Відносини
    scores: Mapped[List["IdealScore"]] = relationship(
        "IdealScore", back_populates="criterion",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<IdealCriterion id={self.id} title={self.title!r} category={self.category}>"

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "category":    self.category,
            "title":       self.title,
            "description": self.description,
            "icon":        self.icon,
            "sort_order":  self.sort_order,
            "is_active":   self.is_active,
        }


# ═══════════════════════════════════════════════════════════════
# IDEAL SCORE
# ═══════════════════════════════════════════════════════════════

class IdealScore(Base):
    """Щоденна оцінка за критерієм ідеального я (0–5)."""
    __tablename__ = "ideal_scores"
    __table_args__ = (
        UniqueConstraint("criterion_id", "score_date", name="uq_ideal_score"),
    )

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    criterion_id: Mapped[int]           = mapped_column(Integer, ForeignKey("ideal_criteria.id", ondelete="CASCADE"), nullable=False)
    score_date:   Mapped[date]          = mapped_column(Date, nullable=False)
    score:        Mapped[int]           = mapped_column(Integer, default=0)  # 0-5
    comment:      Mapped[Optional[str]] = mapped_column(Text)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    # Відносини
    criterion: Mapped["IdealCriterion"] = relationship("IdealCriterion", back_populates="scores")

    def __repr__(self) -> str:
        return f"<IdealScore criterion_id={self.criterion_id} date={self.score_date} score={self.score}>"

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "criterion_id": self.criterion_id,
            "score_date":   self.score_date.isoformat(),
            "score":        self.score,
            "comment":      self.comment,
            # joined fields (якщо criterion eager-loaded)
            "title":        self.criterion.title    if self.criterion else None,
            "icon":         self.criterion.icon     if self.criterion else None,
            "category":     self.criterion.category if self.criterion else None,
            "description":  self.criterion.description if self.criterion else None,
        }


# ═══════════════════════════════════════════════════════════════
# JOURNAL
# ═══════════════════════════════════════════════════════════════

class Journal(Base):
    """Денний запис щоденника."""
    __tablename__ = "journal"

    id:         Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_date: Mapped[date]          = mapped_column(Date, nullable=False, unique=True)
    mood:       Mapped[int]           = mapped_column(Integer, default=3)    # 1-5
    energy:     Mapped[int]           = mapped_column(Integer, default=3)    # 1-5
    content:    Mapped[Optional[str]] = mapped_column(Text)
    wins:       Mapped[Optional[str]] = mapped_column(Text)
    tomorrow:   Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Journal date={self.entry_date} mood={self.mood}>"

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "entry_date": self.entry_date.isoformat(),
            "mood":       self.mood,
            "energy":     self.energy,
            "content":    self.content,
            "wins":       self.wins,
            "tomorrow":   self.tomorrow,
        }


# ═══════════════════════════════════════════════════════════════
# GOAL
# ═══════════════════════════════════════════════════════════════

class Goal(Base):
    """Особиста ціль."""
    __tablename__ = "goals"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:       Mapped[str]           = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category:    Mapped[str]           = mapped_column(String(40),  default="general")
    deadline:    Mapped[Optional[date]] = mapped_column(Date)
    status:      Mapped[str]           = mapped_column(String(20),  default="active")  # active|done|paused
    progress:    Mapped[int]           = mapped_column(Integer, default=0)             # 0-100
    created_at:  Mapped[date]          = mapped_column(Date, default=date.today)

    def __repr__(self) -> str:
        return f"<Goal id={self.id} title={self.title!r} status={self.status}>"

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "title":       self.title,
            "description": self.description,
            "category":    self.category,
            "deadline":    self.deadline.isoformat() if self.deadline else None,
            "status":      self.status,
            "progress":    self.progress,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }