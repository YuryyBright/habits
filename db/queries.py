"""
SelfMaster - Data Access Layer (SQLAlchemy ORM)
Всі CRUD-операції та запити через ORM-сесії.
Публічний API повністю сумісний зі старим queries.py:
  ті самі назви функцій, ті самі типи повернення (dict / list[dict]).
"""
import calendar
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, and_, or_

from .database import get_session
from .models import Goal, Habit, HabitLog, IdealCriterion, IdealScore, Journal
from config import STATS_HABIT_DAYS


# ═══════════════════════════════════════════════════════════════
# HABITS
# ═══════════════════════════════════════════════════════════════

def get_habits(active_only: bool = True) -> list[dict]:
    with get_session() as s:
        q = s.query(Habit)
        if active_only:
            q = q.filter(Habit.is_active.is_(True))
        habits = q.order_by(Habit.sort_order, Habit.id).all()
        return [h.to_dict() for h in habits]


def get_habit_by_id(habit_id: int) -> Optional[dict]:
    with get_session() as s:
        h = s.get(Habit, habit_id)
        return h.to_dict() if h else None


def add_habit(
    name: str,
    emoji: str = "⭐",
    htype: str = "toggle",
    unit: Optional[str] = None,
    category: str = "general",
    goal_value: Optional[float] = None,
    is_negative: bool = False,
    color: str = "#c8f135",
) -> int:
    """Додає нову звичку. Повертає id."""
    with get_session() as s:
        max_order = s.query(func.coalesce(func.max(Habit.sort_order), 0)).scalar() or 0
        habit = Habit(
            name=name, emoji=emoji, type=htype, unit=unit,
            category=category, goal_value=goal_value,
            is_negative=is_negative, color=color,
            sort_order=max_order + 1,
        )
        s.add(habit)
        s.flush()
        return habit.id


def update_habit(habit_id: int, **kwargs) -> None:
    allowed = {
        "name", "emoji", "type", "unit", "category",
        "goal_value", "is_negative", "color", "sort_order", "is_active",
    }
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    with get_session() as s:
        habit = s.get(Habit, habit_id)
        if habit:
            for k, v in fields.items():
                setattr(habit, k, v)


def delete_habit(habit_id: int) -> None:
    with get_session() as s:
        habit = s.get(Habit, habit_id)
        if habit:
            s.delete(habit)


# ═══════════════════════════════════════════════════════════════
# HABIT LOGS
# ═══════════════════════════════════════════════════════════════

def log_habit(
    habit_id: int,
    log_date: date,
    value,
    note: Optional[str] = None,
) -> None:
    """Insert або update запис. value може бути 'done'|'fail'|число."""
    str_value = str(value) if value is not None else None
    with get_session() as s:
        existing = (
            s.query(HabitLog)
            .filter_by(habit_id=habit_id, log_date=log_date)
            .first()
        )
        if existing:
            existing.value = str_value
            existing.note  = note
        else:
            s.add(HabitLog(habit_id=habit_id, log_date=log_date,
                           value=str_value, note=note))


def clear_log(habit_id: int, log_date: date) -> None:
    with get_session() as s:
        entry = (
            s.query(HabitLog)
            .filter_by(habit_id=habit_id, log_date=log_date)
            .first()
        )
        if entry:
            s.delete(entry)


def get_logs_for_month(year: int, month: int) -> dict[int, dict[int, str]]:
    """Повертає {habit_id: {day: value}} для заданого місяця."""
    from_date = date(year, month, 1)
    to_date   = date(year, month, calendar.monthrange(year, month)[1])

    with get_session() as s:
        rows = (
            s.query(HabitLog.habit_id, HabitLog.log_date, HabitLog.value)
            .filter(HabitLog.log_date.between(from_date, to_date))
            .all()
        )

    result: dict[int, dict[int, str]] = {}
    for habit_id, log_date_val, value in rows:
        result.setdefault(habit_id, {})[log_date_val.day] = value
    return result


def get_logs_for_date(log_date: date) -> list[dict]:
    with get_session() as s:
        rows = (
            s.query(HabitLog, Habit)
            .join(Habit, Habit.id == HabitLog.habit_id)
            .filter(HabitLog.log_date == log_date)
            .all()
        )
        return [
            {**log.to_dict(), **habit.to_dict()}
            for log, habit in rows
        ]


def get_habit_streak(habit_id: int) -> tuple[int, int]:
    """Повертає (поточний_streak, найкращий_streak)."""
    habit_data = get_habit_by_id(habit_id)
    if not habit_data:
        return 0, 0

    is_negative = habit_data["is_negative"]

    with get_session() as s:
        rows = (
            s.query(HabitLog.log_date, HabitLog.value)
            .filter(HabitLog.habit_id == habit_id)
            .order_by(HabitLog.log_date)
            .all()
        )

    log_dict = {r.log_date: r.value for r in rows}

    def _is_done(val):
        if val is None or val == "fail":
            return False
        if val == "done":
            return True
        try:
            n = float(val)
            return (n == 0) if is_negative else (n > 0)
        except (ValueError, TypeError):
            return False

    # Поточний streak назад від сьогодні
    today = date.today()
    cur, check = 0, today
    while True:
        if _is_done(log_dict.get(check)):
            cur   += 1
            check -= timedelta(days=1)
        else:
            break

    # Найкращий streak по всій історії
    best, run = 0, 0
    for r in rows:
        if _is_done(r.value):
            run  += 1
            best  = max(best, run)
        else:
            run = 0

    return cur, best


def get_habit_history(habit_id: int, days: int = STATS_HABIT_DAYS) -> list[tuple[str, str]]:
    from_date = date.today() - timedelta(days=days)
    with get_session() as s:
        rows = (
            s.query(HabitLog.log_date, HabitLog.value)
           .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.log_date >= from_date,
            )
            .order_by(HabitLog.log_date)
            .all()
        )
    return [(r.log_date.isoformat(), r.value) for r in rows]


# ═══════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════

def get_monthly_stats(year: int, month: int) -> list[dict]:
    habits     = get_habits()
    logs       = get_logs_for_month(year, month)
    today      = date.today()
    days_total = calendar.monthrange(year, month)[1]
    is_current = (today.year == year and today.month == month)
    passed     = today.day if is_current else days_total

    result = []
    for h in habits:
        hlog   = logs.get(h["id"], {})
        done   = 0
        logged = 0

        for d in range(1, passed + 1):
            val = hlog.get(d)
            if val is None:
                continue
            logged += 1
            if val == "done":
                done += 1
            elif val != "fail":
                try:
                    n = float(val)
                    if h["is_negative"]:
                        done += int(n == 0)
                    else:
                        done += int(n > 0)
                except (ValueError, TypeError):
                    pass

        pct           = round(done / logged * 100) if logged else 0
        cur_s, best_s = get_habit_streak(h["id"])
        result.append({
            **h,
            "done":        done,
            "logged":      logged,
            "pct":         pct,
            "cur_streak":  cur_s,
            "best_streak": best_s,
        })
    return result


def _value_is_done(value: Optional[str], is_negative: bool) -> bool:
    if value is None or value == "fail":
        return False
    if value == "done":
        return True
    try:
        n = float(value)
        return (n == 0) if is_negative else (n > 0)
    except (ValueError, TypeError):
        return False


def get_overall_stats() -> dict:
    with get_session() as s:
        total = s.query(func.count(HabitLog.id)).scalar() or 0
        rows  = (
            s.query(HabitLog.value, Habit.is_negative)
            .join(Habit, Habit.id == HabitLog.habit_id)
            .all()
        )
        days_tracked = (
            s.query(func.count(func.distinct(HabitLog.log_date))).scalar() or 0
        )

    done_count = sum(1 for val, is_neg in rows if _value_is_done(val, is_neg))
    pct        = round(done_count / total * 100) if total else 0

    return {
        "total":        total,
        "done":         done_count,
        "pct":          pct,
        "days_tracked": days_tracked,
    }


def get_weekly_data(weeks: int = 12) -> list[dict]:
    today  = date.today()
    result = []

    with get_session() as s:
        for w in range(weeks - 1, -1, -1):
            week_end   = today - timedelta(days=today.weekday() + 7 * w)
            week_start = week_end - timedelta(days=6)

            rows = (
                s.query(HabitLog.value, Habit.is_negative)
                .join(Habit, Habit.id == HabitLog.habit_id)
                .filter(HabitLog.log_date.between(week_start, week_end))
                .all()
            )

            total = len(rows)
            done  = sum(1 for val, is_neg in rows if _value_is_done(val, is_neg))
            pct   = round(done / total * 100) if total else 0

            result.append({
                "label": week_start.strftime("%d.%m"),
                "pct":   pct,
                "done":  done,
                "total": total,
            })

    return result


# ═══════════════════════════════════════════════════════════════
# IDEAL SELF
# ═══════════════════════════════════════════════════════════════

def get_ideal_criteria(active_only: bool = True) -> list[dict]:
    with get_session() as s:
        q = s.query(IdealCriterion)
        if active_only:
            q = q.filter(IdealCriterion.is_active.is_(True))
        return [r.to_dict() for r in q.order_by(
            IdealCriterion.category, IdealCriterion.sort_order
        ).all()]


def add_ideal_criterion(
    category: str,
    title: str,
    icon: str = "🎯",
    description: Optional[str] = None,
) -> int:
    with get_session() as s:
        max_order = (
            s.query(func.coalesce(func.max(IdealCriterion.sort_order), 0)).scalar() or 0
        )
        crit = IdealCriterion(
            category=category, title=title, icon=icon,
            description=description, sort_order=max_order + 1,
        )
        s.add(crit)
        s.flush()
        return crit.id


def update_ideal_criterion(crit_id: int, **kwargs) -> None:
    allowed = {"category", "title", "icon", "description", "sort_order", "is_active"}
    fields  = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    with get_session() as s:
        crit = s.get(IdealCriterion, crit_id)
        if crit:
            for k, v in fields.items():
                setattr(crit, k, v)


def delete_ideal_criterion(crit_id: int) -> None:
    with get_session() as s:
        crit = s.get(IdealCriterion, crit_id)
        if crit:
            s.delete(crit)


def score_ideal(
    criterion_id: int,
    score_date: date,
    score: int,
    comment: Optional[str] = None,
) -> None:
    with get_session() as s:
        existing = (
            s.query(IdealScore)
            .filter_by(criterion_id=criterion_id, score_date=score_date)
            .first()
        )
        if existing:
            existing.score   = score
            existing.comment = comment
        else:
            s.add(IdealScore(
                criterion_id=criterion_id, score_date=score_date,
                score=score, comment=comment,
            ))


def get_ideal_scores_for_date(score_date: date) -> list[dict]:
    with get_session() as s:
        rows = (
            s.query(IdealScore)
            .join(IdealCriterion, IdealCriterion.id == IdealScore.criterion_id)
            .filter(IdealScore.score_date == score_date)
            .all()
        )
        return [r.to_dict() for r in rows]


def get_ideal_weekly_avg(weeks: int = 8) -> list[dict]:
    today  = date.today()
    result = []
    with get_session() as s:
        for w in range(weeks - 1, -1, -1):
            week_end   = today - timedelta(days=today.weekday() + 7 * w)
            week_start = week_end - timedelta(days=6)
            avg = (
                s.query(func.avg(IdealScore.score))
                .filter(IdealScore.score_date.between(week_start, week_end))
                .scalar()
            )
            result.append({"label": week_start.strftime("%d.%m"), "avg": round(avg or 0, 1)})
    return result


def get_ideal_category_stats(days: int = 30) -> list[dict]:
    from_date = date.today() - timedelta(days=days)
    with get_session() as s:
        rows = (
            s.query(
                IdealCriterion.category,
                func.avg(IdealScore.score).label("avg_score"),
                func.count(IdealScore.id).label("cnt"),
            )
            .join(IdealCriterion, IdealCriterion.id == IdealScore.criterion_id)
            .filter(IdealScore.score_date >= from_date)
            .group_by(IdealCriterion.category)
            .all()
        )
    return [
        {"category": r.category, "avg_score": round(r.avg_score or 0, 2), "cnt": r.cnt}
        for r in rows
    ]


# ═══════════════════════════════════════════════════════════════
# JOURNAL
# ═══════════════════════════════════════════════════════════════

def save_journal(
    entry_date: date,
    mood: int,
    energy: int,
    content: str,
    wins: Optional[str] = None,
    tomorrow: Optional[str] = None,
) -> None:
    with get_session() as s:
        entry = s.query(Journal).filter_by(entry_date=entry_date).first()
        if entry:
            entry.mood     = mood
            entry.energy   = energy
            entry.content  = content
            entry.wins     = wins
            entry.tomorrow = tomorrow
        else:
            s.add(Journal(
                entry_date=entry_date, mood=mood, energy=energy,
                content=content, wins=wins, tomorrow=tomorrow,
            ))


def get_journal(entry_date: date) -> Optional[dict]:
    with get_session() as s:
        entry = s.query(Journal).filter_by(entry_date=entry_date).first()
        return entry.to_dict() if entry else None


def get_journal_recent(limit: int = 30) -> list[dict]:
    with get_session() as s:
        rows = (
            s.query(Journal)
            .order_by(Journal.entry_date.desc())
            .limit(limit)
            .all()
        )
        return [r.to_dict() for r in rows]


def get_mood_data(days: int = 30) -> list[dict]:
    from_date = date.today() - timedelta(days=days)
    with get_session() as s:
        rows = (
            s.query(Journal.entry_date, Journal.mood, Journal.energy)
            .filter(Journal.entry_date >= from_date)
            .order_by(Journal.entry_date)
            .all()
        )
    return [
        {"entry_date": r.entry_date.isoformat(), "mood": r.mood, "energy": r.energy}
        for r in rows
    ]


# ═══════════════════════════════════════════════════════════════
# GOALS
# ═══════════════════════════════════════════════════════════════

def get_goals(status: Optional[str] = None) -> list[dict]:
    with get_session() as s:
        q = s.query(Goal)
        if status:
            q = q.filter(Goal.status == status)
        return [r.to_dict() for r in q.order_by(Goal.created_at.desc()).all()]


def add_goal(
    title: str,
    description: Optional[str] = None,
    category: str = "general",
    deadline: Optional[date] = None,
) -> int:
    with get_session() as s:
        goal = Goal(title=title, description=description,
                    category=category, deadline=deadline)
        s.add(goal)
        s.flush()
        return goal.id


def update_goal(goal_id: int, **kwargs) -> None:
    allowed = {"title", "description", "category", "deadline", "status", "progress"}
    fields  = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    with get_session() as s:
        goal = s.get(Goal, goal_id)
        if goal:
            for k, v in fields.items():
                setattr(goal, k, v)


def delete_goal(goal_id: int) -> None:
    with get_session() as s:
        goal = s.get(Goal, goal_id)
        if goal:
            s.delete(goal)