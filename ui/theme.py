"""SelfMaster — Theme v2.1 (Compact Clean Light)"""

# ── Palette ───────────────────────────────────────────────────────────────────
BG         = "#f8f9fc"
SURFACE    = "#ffffff"
SURFACE2   = "#f1f5f9"
SURFACE3   = "#e2e8f0"

BORDER     = "#e2e8f0"      # тонший, майже непомітний

ACCENT     = "#6366f1"
ACCENT_L   = "#818cf8"
ACCENT2    = "#ec4899"
ACCENT3    = "#06b6d4"
ACCENT4    = "#8b5cf6"

TEXT       = "#0f172a"
TEXT_DIM   = "#64748b"
TEXT_MID   = "#475569"

DONE       = "#16a34a"
FAIL       = "#dc2626"
STREAK     = "#d97706"
SUCCESS    = "#059669"

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

MOOD_COLORS = {1: "#dc2626", 2: "#f97316", 3: "#ca8a04", 4: "#65a30d", 5: "#16a34a"}
MOOD_LABELS = {1: "😞 Погано", 2: "😕 Не дуже", 3: "😐 Нормально", 4: "😊 Добре", 5: "😄 Чудово"}

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_MAIN   = ("Segoe UI", 9)
FONT_BOLD   = ("Segoe UI", 9, "bold")
FONT_TITLE  = ("Segoe UI", 12, "bold")
FONT_BIG    = ("Segoe UI", 18, "bold")
FONT_MONO   = ("Consolas", 8)
FONT_MONO_B = ("Consolas", 8, "bold")


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
                    font=FONT_BOLD, padding=(8, 5), relief="flat", borderwidth=0)
    style.map("TButton",
              background=[("active", SURFACE3), ("pressed", SURFACE3)],
              foreground=[("active", ACCENT)])

    # ── Scrollbar — тонкий і ненав'язливий ───────────────────────────────
    style.configure("TScrollbar",
                    background=SURFACE2,
                    troughcolor=BG,
                    borderwidth=0,
                    arrowsize=0,          # прибрати стрілки
                    relief="flat",
                    width=4)              # дуже тонкий
    style.map("TScrollbar",
              background=[("active", ACCENT_L), ("!active", SURFACE3)])
    style.layout("Vertical.TScrollbar", [
        ("Vertical.Scrollbar.trough", {
            "sticky": "ns",
            "children": [("Vertical.Scrollbar.thumb", {"sticky": "nswe"})]
        })
    ])

    style.configure("TCombobox", fieldbackground=SURFACE, background=SURFACE,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground="white", bordercolor=BORDER, arrowcolor=TEXT_DIM,
                    padding=(4, 4))
    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT,
                    bordercolor=BORDER, insertcolor=TEXT)
    style.configure("TScale", background=BG, troughcolor=SURFACE2,
                    sliderrelief="flat", sliderlength=14)
    style.configure("Horizontal.TProgressbar", troughcolor=SURFACE2,
                    background=ACCENT, borderwidth=0, thickness=4)
    style.configure("TCheckbutton", background=BG, foreground=TEXT,
                    indicatorcolor=SURFACE, font=FONT_MAIN)
    style.map("TCheckbutton",
              indicatorcolor=[("selected", ACCENT), ("active", ACCENT_L)],
              background=[("active", BG)])
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_BOLD, padding=(12, 8))
    style.map("TNotebook.Tab",
              background=[("selected", SURFACE)],
              foreground=[("selected", ACCENT)])
    style.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=26)
    style.configure("Treeview.Heading", background=SURFACE2, foreground=TEXT_DIM,
                    font=FONT_MONO)
    style.map("Treeview", background=[("selected", ACCENT_L)],
              foreground=[("selected", "white")])
    return style


def _hex_fade(hex_color, alpha):
    """Blend hex_color with BG by alpha (0–1)."""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        br, bg_c, bb = int(BG[1:3], 16), int(BG[3:5], 16), int(BG[5:7], 16)
        nr = int(r * alpha + br * (1 - alpha))
        ng = int(g * alpha + bg_c * (1 - alpha))
        nb = int(b * alpha + bb * (1 - alpha))
        return f"#{nr:02x}{ng:02x}{nb:02x}"
    except:
        return SURFACE2