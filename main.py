"""
SelfMaster v2.0 — Головний файл
Запустити: python main.py

Дані зберігаються локально: ~/.selfmaster/data.db (SQLite)
Залежності: тільки Python стандартна бібліотека + tkinter
Опційно: pip install matplotlib  (для графіків)
"""
import tkinter as tk
from tkinter import ttk
import sys, os
from datetime import date
from ui.theme import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db 


class SelfMasterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SelfMaster — Покращення Себе")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.root.configure(bg=BG)

        # Init database (creates ~/.selfmaster/data.db if not exists)
        init_db()

        apply_theme(self.root)
        self._build_ui()

    def _build_ui(self):
        # ── Sidebar ───────────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=SURFACE, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Right border
        tk.Frame(sidebar, bg=BORDER, width=1).pack(side="right", fill="y")

        # ── Logo ─────────────────────────────────────────────────────────
        logo_f = tk.Frame(sidebar, bg=SURFACE, pady=28)
        logo_f.pack(fill="x")

        # Logo dot
        dot = tk.Canvas(logo_f, width=36, height=36, bg=SURFACE,
                        highlightthickness=0)
        dot.pack(pady=(0,8))
        dot.create_oval(3, 3, 33, 33, fill=ACCENT, outline="")
        dot.create_text(18, 18, text="S", fill=TEXT, font=("Segoe UI",16,"bold"))

        tk.Label(logo_f, text="SelfMaster", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI",13,"bold")).pack()
        tk.Label(logo_f, text="Покращення Себе", bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas",8)).pack()

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0,8))

        # ── Nav items ─────────────────────────────────────────────────────
        nav_items = [
            ("📅", "Сьогодні",   "today",  ACCENT),
            ("📊", "Місяць",     "month",  ACCENT3),
            ("📈", "Статистика", "stats",  ACCENT2),
            ("🌟", "Ідеал",      "ideal",  ACCENT2),
            ("⚙️", "Звички",     "habits", ACCENT),
            ("🎯", "Цілі",       "goals",  "#f59e0b"),
        ]

        self._nav_btns = {}
        self._active_tab = tk.StringVar(value="today")

        for emoji, label, key, color in nav_items:
            btn = self._make_nav_btn(sidebar, emoji, label, key, color)
            self._nav_btns[key] = (btn, color)

        # ── Bottom info ───────────────────────────────────────────────────
        tk.Frame(sidebar, bg=BORDER, height=1).pack(side="bottom", fill="x", padx=16, pady=(0,8))
        bottom = tk.Frame(sidebar, bg=SURFACE)
        bottom.pack(side="bottom", fill="x", padx=16, pady=(0,16))

        tk.Label(bottom, text=f"💾 {DB_PATH}", bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas",7), wraplength=185, justify="left").pack(anchor="w")
        tk.Label(bottom, text=f"v2.0  •  {date.today():%d.%m.%Y}",
                 bg=SURFACE, fg=TEXT_DIM, font=("Consolas",8)).pack(anchor="w", pady=(4,0))

        # ── Content area ──────────────────────────────────────────────────
        self._content = tk.Frame(self.root, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        # ── Tabs ──────────────────────────────────────────────────────────
        tab_classes = {
            "today":  TodayTab,
            "month":  MonthTab,
            "stats":  StatsTab,
            "ideal":  IdealTab,
            "habits": HabitsTab,
            "goals":  GoalsTab,
        }
        self._tabs = {}
        for key, cls in tab_classes.items():
            tab = cls(self._content)
            tab.place(relwidth=1, relheight=1)
            self._tabs[key] = tab

        self._switch_tab("today")

    def _make_nav_btn(self, parent, emoji, label, key, color):
        f = tk.Frame(parent, bg=SURFACE, cursor="hand2")
        f.pack(fill="x", padx=10, pady=2)

        # Accent indicator bar (left)
        indicator = tk.Frame(f, bg=SURFACE, width=3)
        indicator.pack(side="left", fill="y")

        inner = tk.Frame(f, bg=SURFACE, padx=12, pady=12)
        inner.pack(side="left", fill="x", expand=True)

        em_lbl = tk.Label(inner, text=emoji, bg=SURFACE,
                          font=("Segoe UI",14))
        em_lbl.pack(side="left", padx=(0,10))

        txt_lbl = tk.Label(inner, text=label, bg=SURFACE, fg=TEXT_DIM,
                           font=("Segoe UI",10,"bold"), anchor="w")
        txt_lbl.pack(side="left", fill="x", expand=True)

        def on_enter(e):
            if self._active_tab.get() != key:
                for w in [f, inner, em_lbl, txt_lbl]:
                    w.configure(bg=SURFACE2)
                indicator.configure(bg=_hex_fade(color, 0.4))

        def on_leave(e):
            if self._active_tab.get() != key:
                for w in [f, inner, em_lbl, txt_lbl]:
                    w.configure(bg=SURFACE)
                indicator.configure(bg=SURFACE)

        def on_click(e):
            self._switch_tab(key)

        for w in [f, inner, em_lbl, txt_lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        f._inner = inner
        f._em = em_lbl
        f._txt = txt_lbl
        f._indicator = indicator
        f._color = color
        return f

    def _switch_tab(self, key):
        old = self._active_tab.get()
        if old in self._nav_btns:
            btn, _ = self._nav_btns[old]
            for w in [btn, btn._inner, btn._em, btn._txt]:
                w.configure(bg=SURFACE)
            btn._txt.configure(fg=TEXT_DIM)
            btn._indicator.configure(bg=SURFACE)

        self._active_tab.set(key)
        btn, color = self._nav_btns[key]
        for w in [btn, btn._inner, btn._em, btn._txt]:
            w.configure(bg=SURFACE2)
        btn._txt.configure(fg=color)
        btn._indicator.configure(bg=color)

        for k, tab in self._tabs.items():
            tab.lift() if k == key else tab.lower()

        if hasattr(self._tabs[key], 'refresh'):
            self._tabs[key].refresh()

    def run(self):
        self.root.mainloop()


def main():
    app = SelfMasterApp()
    app.run()


if __name__ == "__main__":
    main()
