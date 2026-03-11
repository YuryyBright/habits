"""SelfMaster — Theme v2 (Modern Dark-Light Hybrid)"""

# ── Palette ──────────────────────────────────────────────────────────────────
BG         = "#0f0f13"     # Deep dark background
SURFACE    = "#1a1a24"     # Card surface
SURFACE2   = "#22222e"     # Secondary surface
SURFACE3   = "#2a2a38"     # Hover/active surface
BORDER     = "#2e2e3e"     # Subtle borders

# Accent colors (vibrant)
ACCENT     = "#6366f1"     # Indigo
ACCENT_L   = "#818cf8"     # Light indigo (hover)
ACCENT2    = "#ec4899"     # Pink
ACCENT3    = "#06b6d4"     # Cyan
ACCENT4    = "#8b5cf6"     # Violet

TEXT       = "#f1f5f9"     # Primary text
TEXT_DIM   = "#64748b"     # Secondary text
TEXT_MID   = "#94a3b8"     # Medium text

DONE       = "#22c55e"     # Green
FAIL       = "#ef4444"     # Red
STREAK     = "#f59e0b"     # Amber
SUCCESS    = "#10b981"     # Emerald

# Category colors
CATEGORY_COLORS = {
    "physical":  "#22c55e",
    "mental":    "#6366f1",
    "social":    "#ec4899",
    "financial": "#f59e0b",
    "spiritual": "#8b5cf6",
    "other":     "#64748b",
    "health":    "#22c55e",
    "mind":      "#06b6d4",
    "general":   "#64748b",
}
CATEGORY_LABELS = {
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

MOOD_COLORS = {1:"#ef4444", 2:"#f97316", 3:"#f59e0b", 4:"#84cc16", 5:"#22c55e"}
MOOD_LABELS = {1:"😞 Погано", 2:"😕 Не дуже", 3:"😐 Нормально", 4:"😊 Добре", 5:"😄 Чудово"}

# ── Fonts ─────────────────────────────────────────────────────────────────────
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
              background=[("active", SURFACE3)],
              foreground=[("active", ACCENT_L)])
    style.configure("TScrollbar", background=SURFACE2, troughcolor=SURFACE,
                    borderwidth=0, arrowsize=10, relief="flat")
    style.map("TScrollbar", background=[("active", SURFACE3)])
    style.configure("TCombobox", fieldbackground=SURFACE2, background=SURFACE2,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground=TEXT, bordercolor=BORDER, arrowcolor=TEXT_DIM)
    style.configure("TEntry", fieldbackground=SURFACE2, foreground=TEXT,
                    bordercolor=BORDER, insertcolor=TEXT)
    style.configure("TScale", background=BG, troughcolor=SURFACE2,
                    sliderrelief="flat", sliderlength=16)
    style.configure("Horizontal.TProgressbar", troughcolor=SURFACE2,
                    background=ACCENT, borderwidth=0, thickness=4)
    style.configure("TCheckbutton", background=BG, foreground=TEXT_MID,
                    indicatorcolor=SURFACE2, font=FONT_MAIN)
    style.map("TCheckbutton",
              indicatorcolor=[("selected", ACCENT)],
              background=[("active", BG)])
    style.configure("TNotebook", background=SURFACE, borderwidth=0)
    style.configure("TNotebook.Tab", background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_BOLD, padding=(16, 10))
    style.map("TNotebook.Tab",
              background=[("selected", BG)],
              foreground=[("selected", ACCENT)])
    style.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=30)
    style.configure("Treeview.Heading", background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_MONO)
    style.map("Treeview", background=[("selected", SURFACE3)],
              foreground=[("selected", ACCENT_L)])
    return style


def _hex_fade(hex, alpha):
    return "#%02x%02x%02x" % tuple(int(hex[i:i+2], 16) * alpha for i in (1,3,5))