"""
SelfMaster - UI Theme & Styles
Centralized color palette and widget styles.
"""

# ── Colors ──────────────────────────────────────────────────────────────────
BG         = "#0d0d0f"
SURFACE    = "#141417"
SURFACE2   = "#1c1c21"
BORDER     = "#2a2a32"
ACCENT     = "#c8f135"   # lime green
ACCENT2    = "#f13594"   # pink
ACCENT3    = "#35c8f1"   # cyan
TEXT       = "#e8e8f0"
TEXT_DIM   = "#6b6b7e"
DONE       = "#c8f135"
FAIL       = "#f13544"
STREAK     = "#ffb830"
SUCCESS    = "#22c55e"

CATEGORY_COLORS = {
    "physical":  "#c8f135",
    "mental":    "#35c8f1",
    "social":    "#f13594",
    "financial": "#ffb830",
    "spiritual": "#a78bfa",
    "other":     "#6b6b7e",
    "health":    "#c8f135",
    "mind":      "#35c8f1",
    "general":   "#6b6b7e",
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

MOOD_COLORS = {1: "#f13544", 2: "#ffb830", 3: "#35c8f1", 4: "#c8f135", 5: "#22c55e"}
MOOD_LABELS = {1: "😞 Погано", 2: "😕 Не дуже", 3: "😐 Нормально", 4: "😊 Добре", 5: "😄 Чудово"}

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BIG   = ("Segoe UI", 22, "bold")
FONT_MONO  = ("Consolas", 9)

# ── tkinter style config ────────────────────────────────────────────────────
def apply_theme(root):
    """Apply dark theme to tkinter root and ttk styles."""
    import tkinter as tk
    from tkinter import ttk

    root.configure(bg=BG)

    style = ttk.Style(root)
    style.theme_use("clam")

    # General
    style.configure(".", background=BG, foreground=TEXT,
                    font=FONT_MAIN, borderwidth=0, relief="flat")

    # Notebook (tabs)
    style.configure("TNotebook", background=SURFACE, borderwidth=0, tabmargins=0)
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
    style.configure("Dim.TLabel", foreground=TEXT_DIM, font=FONT_MONO)
    style.configure("Accent.TLabel", foreground=ACCENT, font=FONT_BOLD)
    style.configure("Big.TLabel", font=FONT_BIG, foreground=ACCENT)

    # Button
    style.configure("TButton", background=SURFACE2, foreground=TEXT,
                    font=FONT_BOLD, relief="flat", borderwidth=1,
                    padding=(12, 6))
    style.map("TButton",
              background=[("active", BORDER), ("pressed", BG)],
              foreground=[("active", ACCENT)])
    style.configure("Accent.TButton", background=ACCENT, foreground=BG,
                    font=FONT_BOLD)
    style.map("Accent.TButton",
              background=[("active", "#a8d120")])
    style.configure("Danger.TButton", background="#3a1a1a", foreground=FAIL)
    style.map("Danger.TButton",
              background=[("active", "#5a2a2a")])

    # Entry
    style.configure("TEntry", fieldbackground=SURFACE2, foreground=TEXT,
                    bordercolor=BORDER, insertcolor=TEXT, font=FONT_MAIN)

    # Scrollbar
    style.configure("TScrollbar", background=SURFACE2, troughcolor=SURFACE,
                    borderwidth=0, arrowsize=12, relief="flat")

    # Scale
    style.configure("TScale", background=BG, troughcolor=SURFACE2,
                    sliderrelief="flat")

    # Combobox
    style.configure("TCombobox", fieldbackground=SURFACE2, background=SURFACE2,
                    foreground=TEXT, selectbackground=BORDER,
                    selectforeground=TEXT, bordercolor=BORDER)

    # Treeview
    style.configure("Treeview",
                    background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=32,
                    borderwidth=0, font=FONT_MAIN)
    style.configure("Treeview.Heading",
                    background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_MONO, relief="flat", borderwidth=0)
    style.map("Treeview",
              background=[("selected", BORDER)],
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
                    indicatorcolor=SURFACE2, font=FONT_MAIN)
    style.map("TCheckbutton",
              indicatorcolor=[("selected", ACCENT)])

    return style
