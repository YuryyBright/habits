"""
SelfMaster - Центральний конфіг
Всі налаштування застосунку в одному місці.
"""
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# ШЛЯХИ
# ═══════════════════════════════════════════════════════════════

APP_DIR   = Path.home() / ".selfmaster"
DB_PATH   = APP_DIR / "data.db"
LOG_PATH  = APP_DIR / "app.log"
BACKUP_DIR = APP_DIR / "backups"


# ═══════════════════════════════════════════════════════════════
# БАЗА ДАНИХ
# ═══════════════════════════════════════════════════════════════

# SQLAlchemy URL. Замінити на postgresql://user:pass@host/db якщо потрібно.
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Розмір пулу з'єднань (для SQLite StaticPool, для інших — 5-10)
DB_POOL_SIZE    = 5
DB_POOL_TIMEOUT = 30     # секунд
DB_ECHO_SQL     = False  # True = виводити SQL у консоль (debug)


# ═══════════════════════════════════════════════════════════════
# ЗАСТОСУНОК
# ═══════════════════════════════════════════════════════════════

APP_NAME    = "SelfMaster"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "selfmaster"

# Вікно
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 820
WINDOW_MIN_W  = 900
WINDOW_MIN_H  = 600

# Авто-збереження щоденника (секунди)
AUTOSAVE_INTERVAL_SEC = 30

# Автооновлення UI (мілісекунди)
UI_REFRESH_MS = 60_000


# ═══════════════════════════════════════════════════════════════
# ЗВИЧКИ — дефолтні значення
# ═══════════════════════════════════════════════════════════════

DEFAULT_HABIT_COLOR  = "#c8f135"
DEFAULT_HABIT_EMOJI  = "⭐"
DEFAULT_HABIT_TYPE   = "toggle"   # toggle | number

HABIT_TYPES = {
    "toggle": "Так/Ні",
    "number": "Числове",
}

HABIT_CATEGORIES = {
    "health":   "❤️ Здоров'я",
    "mind":     "🧠 Розум",
    "physical": "💪 Фізичне",
    "social":   "🤝 Соціальне",
    "financial":"💰 Фінанси",
    "other":    "📌 Інше",
}

# Початковий набір звичок (seed)
SEED_HABITS = [
    dict(name="Спорт / Тренування", emoji="💪", type="toggle", unit=None,
         category="health", goal_value=None, is_negative=False, color="#c8f135", sort_order=1),
    dict(name="Читання",            emoji="📚", type="number", unit="стор.",
         category="mind",   goal_value=20.0,  is_negative=False, color="#35c8f1", sort_order=2),
    dict(name="Медитація",          emoji="🧘", type="toggle", unit=None,
         category="mind",   goal_value=None,  is_negative=False, color="#f13594", sort_order=3),
    dict(name="Вода (склянки)",     emoji="💧", type="number", unit="скл.",
         category="health", goal_value=8.0,   is_negative=False, color="#35c8f1", sort_order=4),
    dict(name="Куріння",            emoji="🚬", type="number", unit="сиг.",
         category="health", goal_value=0.0,   is_negative=True,  color="#f13544", sort_order=5),
    dict(name="Сон (годин)",        emoji="😴", type="number", unit="год.",
         category="health", goal_value=8.0,   is_negative=False, color="#ffb830", sort_order=6),
    dict(name="Холодний душ",       emoji="🚿", type="toggle", unit=None,
         category="health", goal_value=None,  is_negative=False, color="#35c8f1", sort_order=7),
    dict(name="Без соцмереж",       emoji="📵", type="toggle", unit=None,
         category="mind",   goal_value=None,  is_negative=False, color="#c8f135", sort_order=8),
]


# ═══════════════════════════════════════════════════════════════
# ІДЕАЛЬНА ЛЮДИНА
# ═══════════════════════════════════════════════════════════════

IDEAL_CATEGORIES = {
    "physical":  "💪 Фізичне",
    "mental":    "🧠 Ментальне",
    "social":    "❤️ Соціальне",
    "financial": "💰 Фінансове",
    "spiritual": "🧘 Духовне",
    "other":     "🎨 Інше",
}

IDEAL_SCORE_LABELS = {
    0: "— Не оцінено",
    1: "1 — Слабко",
    2: "2 — Нижче норми",
    3: "3 — Нормально",
    4: "4 — Добре",
    5: "5 — Відмінно",
}

SEED_CRITERIA = [
    dict(category="physical",  title="Фізична форма",        icon="💪", sort_order=1,
         description="Тренування, здоров'я тіла, витривалість"),
    dict(category="physical",  title="Харчування",            icon="🥗", sort_order=2,
         description="Якість їжі, контроль калорій"),
    dict(category="physical",  title="Сон та відновлення",    icon="😴", sort_order=3,
         description="Режим сну, якість відпочинку"),
    dict(category="mental",    title="Читання / навчання",    icon="📚", sort_order=4,
         description="Постійний розвиток знань та навичок"),
    dict(category="mental",    title="Ментальний стан",       icon="🧠", sort_order=5,
         description="Контроль думок, позитивне мислення"),
    dict(category="mental",    title="Фокус / продуктивність",icon="🎯", sort_order=6,
         description="Глибока робота, відсутність прокрастинації"),
    dict(category="social",    title="Стосунки",              icon="❤️", sort_order=7,
         description="Якість відносин з близькими"),
    dict(category="social",    title="Соціальна активність",  icon="🤝", sort_order=8,
         description="Нетворкінг, нові знайомства"),
    dict(category="financial", title="Фінансова дисципліна",  icon="💰", sort_order=9,
         description="Заощадження, контроль витрат"),
    dict(category="financial", title="Розвиток доходів",      icon="📈", sort_order=10,
         description="Робота над збільшенням доходу"),
    dict(category="spiritual", title="Медитація / духовність",icon="🧘", sort_order=11,
         description="Внутрішній спокій, усвідомленість"),
    dict(category="other",     title="Творчість",             icon="🎨", sort_order=12,
         description="Творчі заняття, хобі"),
]


# ═══════════════════════════════════════════════════════════════
# ЦІЛІ
# ═══════════════════════════════════════════════════════════════

GOAL_CATEGORIES = {
    "health":   "❤️ Здоров'я",
    "career":   "💼 Кар'єра",
    "financial":"💰 Фінанси",
    "personal": "🌱 Особистий розвиток",
    "social":   "🤝 Соціальне",
    "other":    "📌 Інше",
}

GOAL_STATUSES = {
    "active": "● Активна",
    "done":   "✔ Виконано",
    "paused": "⏸ Пауза",
}


# ═══════════════════════════════════════════════════════════════
# СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════

STATS_WEEKLY_PERIODS  = 12   # кількість тижнів для графіку
STATS_HABIT_DAYS      = 90   # горизонт для графіку окремої звички
STATS_MOOD_DAYS       = 30   # горизонт для графіку настрою
STATS_IDEAL_DAYS      = 30   # горизонт для категорій ідеального я

# Пороги % виконання (для кольорів)
PCT_GOOD = 70   # >= зелений
PCT_MID  = 40   # >= жовтий, < зелений; нижче — червоний


# ═══════════════════════════════════════════════════════════════
# НАСТРІЙ
# ═══════════════════════════════════════════════════════════════

MOOD_LABELS = {
    1: "😞 Погано",
    2: "😕 Не дуже",
    3: "😐 Нормально",
    4: "😊 Добре",
    5: "😄 Чудово",
}

MOOD_COLORS = {
    1: "#f13544",
    2: "#ffb830",
    3: "#35c8f1",
    4: "#c8f135",
    5: "#22c55e",
}


# ═══════════════════════════════════════════════════════════════
# ЛОКАЛІЗАЦІЯ (UA)
# ═══════════════════════════════════════════════════════════════

MONTHS_UK = [
    "Січень","Лютий","Березень","Квітень","Травень","Червень",
    "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень",
]
MONTHS_UK_GEN = [
    "Січня","Лютого","Березня","Квітня","Травня","Червня",
    "Липня","Серпня","Вересня","Жовтня","Листопада","Грудня",
]
WEEKDAYS_UK = [
    "Понеділок","Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя",
]