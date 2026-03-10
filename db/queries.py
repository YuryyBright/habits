"""
SelfMaster - Data Access Layer
All CRUD operations and queries.
"""
from datetime import date, datetime, timedelta
from .database import get_connection


# ═══════════════════════════════════════════════════════
# HABITS
# ═══════════════════════════════════════════════════════

def get_habits(active_only=True):
    conn = get_connection()
    q = "SELECT * FROM habits"
    if active_only:
        q += " WHERE is_active=1"
    q += " ORDER BY sort_order, id"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_habit(name, emoji='⭐', htype='toggle', unit=None, category='general',
              goal_value=None, is_negative=0, color='#c8f135'):
    conn = get_connection()
    max_order = conn.execute("SELECT COALESCE(MAX(sort_order),0) FROM habits").fetchone()[0]
    conn.execute("""
        INSERT INTO habits (name, emoji, type, unit, category, goal_value, is_negative, color, sort_order)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (name, emoji, htype, unit, category, goal_value, is_negative, color, max_order + 1))
    conn.commit()
    conn.close()


def update_habit(habit_id, **kwargs):
    allowed = {'name','emoji','type','unit','category','goal_value','is_negative','color','sort_order','is_active'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [habit_id]
    conn = get_connection()
    conn.execute(f"UPDATE habits SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_habit(habit_id):
    conn = get_connection()
    conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════
# HABIT LOGS
# ═══════════════════════════════════════════════════════

def log_habit(habit_id, log_date, value, note=None):
    """Insert or update a habit log entry."""
    if isinstance(log_date, date):
        log_date = log_date.isoformat()
    conn = get_connection()
    conn.execute("""
        INSERT INTO habit_logs (habit_id, log_date, value, note)
        VALUES (?,?,?,?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET value=excluded.value, note=excluded.note
    """, (habit_id, log_date, str(value) if value is not None else None, note))
    conn.commit()
    conn.close()


def clear_log(habit_id, log_date):
    if isinstance(log_date, date):
        log_date = log_date.isoformat()
    conn = get_connection()
    conn.execute("DELETE FROM habit_logs WHERE habit_id=? AND log_date=?", (habit_id, log_date))
    conn.commit()
    conn.close()


def get_logs_for_month(year, month):
    """Returns {habit_id: {day: value}} for given month."""
    from_date = f"{year}-{month:02d}-01"
    to_date = f"{year}-{month:02d}-31"
    conn = get_connection()
    rows = conn.execute("""
        SELECT habit_id, log_date, value
        FROM habit_logs
        WHERE log_date BETWEEN ? AND ?
    """, (from_date, to_date)).fetchall()
    conn.close()
    result = {}
    for r in rows:
        day = int(r['log_date'].split('-')[2])
        if r['habit_id'] not in result:
            result[r['habit_id']] = {}
        result[r['habit_id']][day] = r['value']
    return result


def get_logs_for_date(log_date):
    if isinstance(log_date, date):
        log_date = log_date.isoformat()
    conn = get_connection()
    rows = conn.execute("""
        SELECT hl.*, h.name, h.emoji, h.type, h.unit, h.is_negative, h.goal_value
        FROM habit_logs hl
        JOIN habits h ON h.id = hl.habit_id
        WHERE hl.log_date = ?
    """, (log_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_habit_streak(habit_id):
    """Returns (current_streak, best_streak) for a habit."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT log_date, value FROM habit_logs
        WHERE habit_id=?
        ORDER BY log_date DESC
    """, (habit_id,)).fetchall()
    conn.close()

    habit = get_habit_by_id(habit_id)
    if not habit:
        return 0, 0

    def is_done(val):
        if val is None:
            return False
        if val == 'done':
            return True
        if val == 'fail':
            return False
        try:
            n = float(val)
            return n == 0 if habit['is_negative'] else n > 0
        except:
            return False

    # Current streak
    today = date.today()
    cur = 0
    check = today
    log_dict = {r['log_date']: r['value'] for r in rows}
    while True:
        val = log_dict.get(check.isoformat())
        if is_done(val):
            cur += 1
            check -= timedelta(days=1)
        else:
            break

    # Best streak
    best = 0
    streak = 0
    for r in sorted(rows, key=lambda x: x['log_date']):
        if is_done(r['value']):
            streak += 1
            best = max(best, streak)
        else:
            streak = 0

    return cur, best


def get_habit_by_id(habit_id):
    conn = get_connection()
    r = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
    conn.close()
    return dict(r) if r else None


# ═══════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════

def get_monthly_stats(year, month):
    """Per-habit stats for a given month."""
    habits = get_habits()
    logs = get_logs_for_month(year, month)
    today = date.today()
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    is_current = (today.year == year and today.month == month)
    passed_days = today.day if is_current else days_in_month

    stats = []
    for h in habits:
        hid = h['id']
        hlog = logs.get(hid, {})
        done = 0
        logged = 0
        for d in range(1, passed_days + 1):
            val = hlog.get(d)
            if val is not None:
                logged += 1
                if val == 'done':
                    done += 1
                elif val == 'fail':
                    pass
                else:
                    try:
                        n = float(val)
                        if h['is_negative']:
                            if n == 0:
                                done += 1
                        else:
                            if n > 0:
                                done += 1
                    except:
                        pass
        pct = round(done / logged * 100) if logged else 0
        cur_s, best_s = get_habit_streak(hid)
        stats.append({
            **h,
            'done': done,
            'logged': logged,
            'pct': pct,
            'cur_streak': cur_s,
            'best_streak': best_s,
        })
    return stats


def get_overall_stats():
    """Global statistics across all time."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM habit_logs").fetchone()[0]
    done = conn.execute("""
        SELECT COUNT(*) FROM habit_logs hl
        JOIN habits h ON h.id=hl.habit_id
        WHERE (hl.value='done') OR
              (h.is_negative=0 AND CAST(hl.value AS REAL)>0) OR
              (h.is_negative=1 AND CAST(hl.value AS REAL)=0)
    """).fetchone()[0]
    days_tracked = conn.execute("SELECT COUNT(DISTINCT log_date) FROM habit_logs").fetchone()[0]
    conn.close()
    pct = round(done / total * 100) if total else 0
    return {'total': total, 'done': done, 'pct': pct, 'days_tracked': days_tracked}


def get_weekly_data(weeks=12):
    """Returns weekly completion % for chart."""
    conn = get_connection()
    today = date.today()
    result = []
    for w in range(weeks - 1, -1, -1):
        week_end = today - timedelta(days=today.weekday() + 7 * w)
        week_start = week_end - timedelta(days=6)
        rows = conn.execute("""
            SELECT hl.value, h.is_negative
            FROM habit_logs hl JOIN habits h ON h.id=hl.habit_id
            WHERE hl.log_date BETWEEN ? AND ?
        """, (week_start.isoformat(), week_end.isoformat())).fetchall()
        total = len(rows)
        done = sum(1 for r in rows if (
            r['value'] == 'done' or
            (r['is_negative'] == 0 and _try_float(r['value'], 0) > 0) or
            (r['is_negative'] == 1 and _try_float(r['value'], 1) == 0)
        ))
        pct = round(done / total * 100) if total else 0
        result.append({'label': week_start.strftime('%d.%m'), 'pct': pct, 'done': done, 'total': total})
    conn.close()
    return result


def _try_float(v, default=0):
    try:
        return float(v)
    except:
        return default


def get_habit_history(habit_id, days=90):
    """Returns list of (date, value) for last N days."""
    conn = get_connection()
    from_date = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT log_date, value FROM habit_logs
        WHERE habit_id=? AND log_date >= ?
        ORDER BY log_date
    """, (habit_id, from_date)).fetchall()
    conn.close()
    return [(r['log_date'], r['value']) for r in rows]


# ═══════════════════════════════════════════════════════
# IDEAL SELF
# ═══════════════════════════════════════════════════════

def get_ideal_criteria(active_only=True):
    conn = get_connection()
    q = "SELECT * FROM ideal_criteria"
    if active_only:
        q += " WHERE is_active=1"
    q += " ORDER BY category, sort_order"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_ideal_criterion(category, title, icon='🎯', description=None):
    conn = get_connection()
    max_order = conn.execute("SELECT COALESCE(MAX(sort_order),0) FROM ideal_criteria").fetchone()[0]
    conn.execute("""
        INSERT INTO ideal_criteria (category, title, icon, description, sort_order)
        VALUES (?,?,?,?,?)
    """, (category, title, icon, description, max_order + 1))
    conn.commit()
    conn.close()


def update_ideal_criterion(crit_id, **kwargs):
    allowed = {'category','title','icon','description','sort_order','is_active'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [crit_id]
    conn = get_connection()
    conn.execute(f"UPDATE ideal_criteria SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_ideal_criterion(crit_id):
    conn = get_connection()
    conn.execute("DELETE FROM ideal_criteria WHERE id=?", (crit_id,))
    conn.commit()
    conn.close()


def score_ideal(criterion_id, score_date, score, comment=None):
    if isinstance(score_date, date):
        score_date = score_date.isoformat()
    conn = get_connection()
    conn.execute("""
        INSERT INTO ideal_scores (criterion_id, score_date, score, comment)
        VALUES (?,?,?,?)
        ON CONFLICT(criterion_id, score_date) DO UPDATE SET score=excluded.score, comment=excluded.comment
    """, (criterion_id, score_date, score, comment))
    conn.commit()
    conn.close()


def get_ideal_scores_for_date(score_date):
    if isinstance(score_date, date):
        score_date = score_date.isoformat()
    conn = get_connection()
    rows = conn.execute("""
        SELECT is.*, ic.title, ic.icon, ic.category, ic.description
        FROM ideal_scores is_ , ideal_criteria ic
        WHERE is_.criterion_id = ic.id AND is_.score_date = ?
        -- fix alias
    """, (score_date,)).fetchall()
    # Fix: use proper alias
    rows = conn.execute("""
        SELECT s.*, c.title, c.icon, c.category, c.description
        FROM ideal_scores s
        JOIN ideal_criteria c ON c.id = s.criterion_id
        WHERE s.score_date = ?
    """, (score_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_ideal_weekly_avg(weeks=8):
    """Average ideal self score per week."""
    conn = get_connection()
    today = date.today()
    result = []
    for w in range(weeks - 1, -1, -1):
        week_end = today - timedelta(days=today.weekday() + 7 * w)
        week_start = week_end - timedelta(days=6)
        row = conn.execute("""
            SELECT AVG(score) as avg_score, COUNT(*) as cnt
            FROM ideal_scores
            WHERE score_date BETWEEN ? AND ?
        """, (week_start.isoformat(), week_end.isoformat())).fetchone()
        avg = round(row['avg_score'] or 0, 1)
        result.append({'label': week_start.strftime('%d.%m'), 'avg': avg})
    conn.close()
    return result


def get_ideal_category_stats(days=30):
    """Average score per category for last N days."""
    conn = get_connection()
    from_date = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT c.category, AVG(s.score) as avg_score, COUNT(*) as cnt
        FROM ideal_scores s
        JOIN ideal_criteria c ON c.id = s.criterion_id
        WHERE s.score_date >= ?
        GROUP BY c.category
    """, (from_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════
# JOURNAL
# ═══════════════════════════════════════════════════════

def save_journal(entry_date, mood, energy, content, wins=None, tomorrow=None):
    if isinstance(entry_date, date):
        entry_date = entry_date.isoformat()
    conn = get_connection()
    conn.execute("""
        INSERT INTO journal (entry_date, mood, energy, content, wins, tomorrow)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(entry_date) DO UPDATE SET
            mood=excluded.mood, energy=excluded.energy, content=excluded.content,
            wins=excluded.wins, tomorrow=excluded.tomorrow
    """, (entry_date, mood, energy, content, wins, tomorrow))
    conn.commit()
    conn.close()


def get_journal(entry_date):
    if isinstance(entry_date, date):
        entry_date = entry_date.isoformat()
    conn = get_connection()
    r = conn.execute("SELECT * FROM journal WHERE entry_date=?", (entry_date,)).fetchone()
    conn.close()
    return dict(r) if r else None


def get_journal_recent(limit=30):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM journal ORDER BY entry_date DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mood_data(days=30):
    conn = get_connection()
    from_date = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT entry_date, mood, energy FROM journal
        WHERE entry_date >= ? ORDER BY entry_date
    """, (from_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════
# GOALS
# ═══════════════════════════════════════════════════════

def get_goals(status=None):
    conn = get_connection()
    q = "SELECT * FROM goals"
    if status:
        q += f" WHERE status='{status}'"
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_goal(title, description=None, category='general', deadline=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO goals (title, description, category, deadline)
        VALUES (?,?,?,?)
    """, (title, description, category, deadline))
    conn.commit()
    conn.close()


def update_goal(goal_id, **kwargs):
    allowed = {'title','description','category','deadline','status','progress'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [goal_id]
    conn = get_connection()
    conn.execute(f"UPDATE goals SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_goal(goal_id):
    conn = get_connection()
    conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))
    conn.commit()
    conn.close()
