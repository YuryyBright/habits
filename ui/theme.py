"""
SelfMaster - UI Theme & Styles (Light Version)
Centralized color palette and widget styles for a clean light mode.
"""

# ── Colors ──────────────────────────────────────────────────────────────────
BG         = "#f8f9fa"   # Дуже світлий сірий/білий
SURFACE    = "#ffffff"   # Чистий білий для карток
SURFACE2   = "#f1f3f5"   # Світло-сірий для другорядних елементів
BORDER     = "#dee2e6"   # Колір рамок
ACCENT     = "#4c6ef5"   # Насичений синій (Indigo)
ACCENT2    = "#d63384"   # Рожевий
ACCENT3    = "#15aabf"   # Бірюзовий
TEXT       = "#212529"   # Темно-сірий (майже чорний)
TEXT_DIM   = "#868e96"   # Приглушений текст
DONE       = "#40c057"   # Зелений
FAIL       = "#fa5252"   # Червоний
STREAK     = "#fcc419"   # Золотий/Жовтий
SUCCESS    = "#22c55e"

CATEGORY_COLORS = {
    "physical":  "#51cf66", # Зелений
    "mental":    "#339af0", # Блакитний
    "social":    "#f06595", # Рожевий
    "financial": "#fcc419", # Золотий
    "spiritual": "#845ef7", # Фіолетовий
    "other":     "#adb5bd", # Сірий
    "health":    "#51cf66",
    "mind":      "#339af0",
    "general":   "#adb5bd",
}

CATEGORY_LABELS = {
    "physical":  "Фізичне",
    "mental":    "Ментальне",
    "social":    "Соціальне",
    "financial": "Фінансове",
    "spiritual": "Духовне",
    "other":     "Інше",
    "health":    "Здоров'я",
    "mind":      "Розум",
    "general":   "Загальне",
}

MOOD_COLORS = {1: "#fa5252", 2: "#ff922b", 3: "#fab005", 4: "#94d82d", 5: "#40c057"}
MOOD_LABELS = {1: "😞 Погано", 2: "😕 Не дуже", 3: "😐 Нормально", 4: "😊 Добре", 5: "😄 Чудово"}

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BIG   = ("Segoe UI", 22, "bold")
FONT_MONO  = ("Consolas", 9)

# ── tkinter style config ────────────────────────────────────────────────────
def apply_theme(root):
    """Apply light theme to tkinter root and ttk styles."""
    import tkinter as tk
    from tkinter import ttk

    root.configure(bg=BG)

    style = ttk.Style(root)
    style.theme_use("clam")

    # General
    style.configure(".", background=BG, foreground=TEXT,
                    font=FONT_MAIN, borderwidth=0, relief="flat")

    # Notebook (tabs)
    style.configure("TNotebook", background=SURFACE2, borderwidth=0, tabmargins=0)
    style.configure("TNotebook.Tab",
                    background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_BOLD, padding=(18, 10),
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", BG)],
              foreground=[("selected", ACCENT)],
              expand=[("selected", [0, 0, 0, 0])])

    # Frame
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=SURFACE, relief="flat")
    style.configure("Surface2.TFrame", background=SURFACE2, relief="flat")

    # Label
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_MAIN)
    style.configure("Title.TLabel", font=FONT_TITLE, foreground=TEXT)
    style.configure("Dim.TLabel", foreground=TEXT_DIM, font=FONT_MONO, background=BG)
    style.configure("Accent.TLabel", foreground=ACCENT, font=FONT_BOLD)
    style.configure("Big.TLabel", font=FONT_BIG, foreground=ACCENT)

    # Button
    style.configure("TButton", background=SURFACE2, foreground=TEXT,
                    font=FONT_BOLD, relief="flat", borderwidth=0,
                    padding=(12, 6))
    style.map("TButton",
              background=[("active", BORDER), ("pressed", "#e9ecef")],
              foreground=[("active", ACCENT)])
    
    style.configure("Accent.TButton", background=ACCENT, foreground=SURFACE,
                    font=FONT_BOLD)
    style.map("Accent.TButton",
              background=[("active", "#3b5bdb")]) # Трохи темніший синій при наведенні
    
    style.configure("Danger.TButton", background="#fff5f5", foreground=FAIL)
    style.map("Danger.TButton",
              background=[("active", "#ffe3e3")])

    # Entry
    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT,
                    bordercolor=BORDER, insertcolor=TEXT, font=FONT_MAIN)

    # Scrollbar
    style.configure("TScrollbar", background=BORDER, troughcolor=SURFACE2,
                    borderwidth=0, arrowsize=12, relief="flat")

    # Scale
    style.configure("TScale", background=BG, troughcolor=BORDER,
                    sliderrelief="flat")

    # Combobox
    style.configure("TCombobox", fieldbackground=SURFACE, background=SURFACE,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground=SURFACE, bordercolor=BORDER)

    # Treeview
    style.configure("Treeview",
                    background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=32,
                    borderwidth=1, font=FONT_MAIN, lightcolor=BORDER)
    style.configure("Treeview.Heading",
                    background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_MONO, relief="flat", borderwidth=0)
    style.map("Treeview",
              background=[("selected", "#e7f5ff")], # Світло-блакитне виділення
              foreground=[("selected", ACCENT)])

    # Progressbar
    style.configure("TProgressbar", troughcolor=SURFACE2,
                    background=ACCENT, borderwidth=0, thickness=6)
    style.configure("Pink.TProgressbar", background=ACCENT2)
    style.configure("Cyan.TProgressbar", background=ACCENT3)
    style.configure("Gold.TProgressbar", background=STREAK)

    # Separator
    style.configure("TSeparator", background=BORDER)

    # Checkbutton
    style.configure("TCheckbutton", background=BG, foreground=TEXT,
                    indicatorcolor=SURFACE, font=FONT_MAIN)
    style.map("TCheckbutton",
              indicatorcolor=[("selected", ACCENT)],
              background=[("active", BG)])

    return style