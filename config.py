"""SelfMaster — Central Config"""
from pathlib import Path

APP_DIR    = Path.home() / ".selfmaster"
DB_PATH    = APP_DIR / "data.db"
APP_NAME   = "SelfMaster"
APP_VERSION = "2.0.0"
DB_ECHO_SQL = False
WINDOW_WIDTH  = 1340
WINDOW_HEIGHT = 860
WINDOW_MIN_W  = 1000
WINDOW_MIN_H  = 640
STATS_HABIT_DAYS = 60
DATABASE_URL = f"sqlite:///{DB_PATH}"
MONTHS_UK = ["Січень","Лютий","Березень","Квітень","Травень","Червень",
             "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
MONTHS_UK_GEN = ["Січня","Лютого","Березня","Квітня","Травня","Червня",
                 "Липня","Серпня","Вересня","Жовтня","Листопада","Грудня"]
WEEKDAYS_UK = ["Понеділок","Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]

SEED_HABITS = [
    dict(name="Спорт / Тренування", emoji="💪", type="toggle", unit=None,
         category="health", goal_value=None, is_negative=0, color="#6366f1", sort_order=1),
    dict(name="Читання", emoji="📚", type="number", unit="стор.",
         category="mind", goal_value=20.0, is_negative=0, color="#06b6d4", sort_order=2),
    dict(name="Медитація", emoji="🧘", type="toggle", unit=None,
         category="mind", goal_value=None, is_negative=0, color="#8b5cf6", sort_order=3),
    dict(name="Вода (склянки)", emoji="💧", type="number", unit="скл.",
         category="health", goal_value=8.0, is_negative=0, color="#3b82f6", sort_order=4),
    dict(name="Сон (годин)", emoji="😴", type="number", unit="год.",
         category="health", goal_value=8.0, is_negative=0, color="#f59e0b", sort_order=5),
    dict(name="Холодний душ", emoji="🚿", type="toggle", unit=None,
         category="health", goal_value=None, is_negative=0, color="#14b8a6", sort_order=6),
    dict(name="Без соцмереж", emoji="📵", type="toggle", unit=None,
         category="mind", goal_value=None, is_negative=0, color="#10b981", sort_order=7),
]

SEED_CRITERIA = [
    dict(category="physical", title="Фізична форма", icon="💪", sort_order=1,
         description="Тренування, здоров'я тіла, витривалість"),
    dict(category="physical", title="Харчування", icon="🥗", sort_order=2,
         description="Якість їжі, контроль калорій"),
    dict(category="mental", title="Читання / навчання", icon="📚", sort_order=3,
         description="Постійний розвиток знань та навичок"),
    dict(category="mental", title="Фокус / продуктивність", icon="🎯", sort_order=4,
         description="Глибока робота, відсутність прокрастинації"),
    dict(category="social", title="Стосунки", icon="❤️", sort_order=5,
         description="Якість відносин з близькими"),
    dict(category="financial", title="Фінансова дисципліна", icon="💰", sort_order=6,
         description="Заощадження, контроль витрат"),
    dict(category="spiritual", title="Медитація / духовність", icon="🧘", sort_order=7,
         description="Внутрішній спокій, усвідомленість"),
]
