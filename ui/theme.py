"""SelfMaster — Theme v2 Light (Modern Clean Light)"""

# ── Palette ──────────────────────────────────────────────────────────────────
BG         = "#f8f9fc"     # Світлий чистий фон
SURFACE    = "#ffffff"     # Білий для карток / основних поверхонь
SURFACE2   = "#f1f5f9"     # Дуже світлий сірий для другого рівня
SURFACE3   = "#e2e8f0"     # Hover / active / розділювачі

BORDER     = "#cbd5e1"     # М'які межі

# Accent colors (залишив майже ті самі, але трохи м'якші тони)
ACCENT     = "#6366f1"     # Indigo (головний акцент)
ACCENT_L   = "#818cf8"     # Light indigo (hover)
ACCENT2    = "#ec4899"     # Pink
ACCENT3    = "#06b6d4"     # Cyan
ACCENT4    = "#8b5cf6"     # Violet

TEXT       = "#0f172a"     # Майже чорний — дуже добре читається
TEXT_DIM   = "#64748b"     # Сірий для другорядного тексту
TEXT_MID   = "#475569"     # Трохи темніший сірий

DONE       = "#16a34a"     # Зелений (трохи темніший для контрасту)
FAIL       = "#dc2626"     # Червоний
STREAK     = "#d97706"     # Темніший amber
SUCCESS    = "#059669"     # Emerald

# Category colors — зроблено трохи яскравішими/насиченішими
CATEGORY_COLORS = {
    "physical":  "#16a34a",
    "mental":    "#6366f1",
    "social":    "#db2777",
    "financial": "#d97706",
    "spiritual": "#7c3aed",
    "other":     "#6b7280",
    "health":    "#16a34a",
    "mind":      "#0891b2",
    "general":   "#6b7280",
}
CATEGORY_LABELS = {     # без змін
    "physical":  "💪 Фізичне",
    "mental":    "🧠 Ментальне",
    "social":    "❤️ Соціальне",
    "financial": "💰 Фінансове",
    "spiritual": "🧘 Духовне",
    "other":     "🎨 Інше",
    "health":    "❤️ Здоров'я",
    "mind":      "🧠 Розум",
    "general":   "📌 Загальне",
}

MOOD_COLORS = {
    1: "#dc2626",   # Погано
    2: "#f97316",
    3: "#ca8a04",
    4: "#65a30d",
    5: "#16a34a"    # Чудово
}
MOOD_LABELS = {         # без змін
    1: "😞 Погано",
    2: "😕 Не дуже",
    3: "😐 Нормально",
    4: "😊 Добре",
    5: "😄 Чудово"
}

# ── Fonts ─────────────────────────────────────────────────────────────────────
# Залишаємо ті самі, бо вони універсальні
FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_BIG   = ("Segoe UI", 20, "bold")
FONT_MONO  = ("Consolas", 9)
FONT_MONO_B = ("Consolas", 9, "bold")


def apply_theme(root):
    import tkinter as tk
    from tkinter import ttk
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT, font=FONT_MAIN,
                    borderwidth=0, relief="flat", troughcolor=SURFACE2)
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("TButton", background=SURFACE2, foreground=TEXT,
                    font=FONT_BOLD, padding=(10,6), relief="flat", borderwidth=0)
    style.map("TButton",
              background=[("active", SURFACE3), ("pressed", SURFACE3)],
              foreground=[("active", ACCENT)])
    style.configure("TScrollbar", background=SURFACE2, troughcolor=BG,
                    borderwidth=0, arrowsize=10, relief="flat")
    style.map("TScrollbar", background=[("active", SURFACE3)])
    style.configure("TCombobox", fieldbackground=SURFACE, background=SURFACE,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground="white", bordercolor=BORDER, arrowcolor=TEXT_DIM)
    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT,
                    bordercolor=BORDER, insertcolor=TEXT)
    style.configure("TScale", background=BG, troughcolor=SURFACE2,
                    sliderrelief="flat", sliderlength=16)
    style.configure("Horizontal.TProgressbar", troughcolor=SURFACE2,
                    background=ACCENT, borderwidth=0, thickness=5)
    style.configure("TCheckbutton", background=BG, foreground=TEXT,
                    indicatorcolor=SURFACE, font=FONT_MAIN)
    style.map("TCheckbutton",
              indicatorcolor=[("selected", ACCENT), ("active", ACCENT_L)],
              background=[("active", BG)])
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_BOLD, padding=(16, 10))
    style.map("TNotebook.Tab",
              background=[("selected", SURFACE)],
              foreground=[("selected", ACCENT)])
    style.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=30)
    style.configure("Treeview.Heading", background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_MONO)
    style.map("Treeview", background=[("selected", ACCENT_L)],
              foreground=[("selected", "white")])

    return style


def _hex_fade(hex_color, alpha):
    """Та сама функція — працює і зі світлим фоном"""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        # Змішуємо з BG (світлим фоном)
        br, bg_color, bb = int(BG[1:3], 16), int(BG[3:5], 16), int(BG[5:7], 16)
        nr = int(r * alpha + br * (1 - alpha))
        ng = int(g * alpha + bg_color * (1 - alpha))
        nb = int(b * alpha + bb * (1 - alpha))
        return f"#{nr:02x}{ng:02x}{nb:02x}"
    except:
        return SURFACE2