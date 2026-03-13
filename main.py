"""
SelfMaster v2.0 — Головний файл
Запустити: python main.py
"""
import tkinter as tk
from tkinter import ttk
import sys, os
from datetime import date
from ui.theme import *
from ui.theme import _hex_fade
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.tab_today import TodayTab
from ui.tab_month import MonthTab
from ui.tab_stats import StatsTab
from ui.tab_ideal import IdealTab
from ui.tab_habits import HabitsTab
from ui.tab_goals import GoalsTab

from db import init_db
from config import *


class SelfMasterApp:
    def __init__(self):
        self.root = tk.Tk()

        # ── Frameless / borderless window ─────────────────────────────────
        self.root.overrideredirect(True)          # прибрати стандартний titlebar
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+80+40")
        self.root.minsize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.root.configure(bg=BG)

        # Для drag по кастомному titlebar
        self._drag_x = 0
        self._drag_y = 0

        init_db()
        apply_theme(self.root)
        self._build_ui()

        # Розгортання на весь екран (опціонально — закоментуй якщо не треба)
        # self.root.state("zoomed")

    # ── Drag support ──────────────────────────────────────────────────────
    def _start_drag(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_drag(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _toggle_maximize(self, event=None):
        if self.root.winfo_width() >= self.root.winfo_screenwidth() - 10:
            self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+80+40")
        else:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")

    def _build_ui(self):
        # ── Custom Title Bar ──────────────────────────────────────────────
        titlebar = tk.Frame(self.root, bg=SURFACE, height=42)
        titlebar.pack(side="top", fill="x")
        titlebar.pack_propagate(False)

        # Нижня межа
        tk.Frame(titlebar, bg=BORDER, height=1).pack(side="bottom", fill="x")

        # Drag bindings
        titlebar.bind("<ButtonPress-1>", self._start_drag)
        titlebar.bind("<B1-Motion>", self._do_drag)
        titlebar.bind("<Double-Button-1>", self._toggle_maximize)

        # Logo dot
        dot = tk.Canvas(titlebar, width=22, height=22, bg=SURFACE,
                        highlightthickness=0)
        dot.pack(side="left", padx=(14, 6), pady=10)
        dot.create_oval(2, 2, 20, 20, fill=ACCENT, outline="")
        dot.create_text(11, 11, text="S", fill="white", font=("Segoe UI", 9, "bold"))
        dot.bind("<ButtonPress-1>", self._start_drag)
        dot.bind("<B1-Motion>", self._do_drag)

        title_lbl = tk.Label(titlebar, text="SelfMaster", bg=SURFACE, fg=TEXT,
                             font=("Segoe UI", 10, "bold"))
        title_lbl.pack(side="left")
        title_lbl.bind("<ButtonPress-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>", self._do_drag)
        title_lbl.bind("<Double-Button-1>", self._toggle_maximize)

        date_lbl = tk.Label(titlebar, text=f"  •  {date.today():%d.%m.%Y}",
                            bg=SURFACE, fg=TEXT_DIM, font=("Consolas", 9))
        date_lbl.pack(side="left")
        date_lbl.bind("<ButtonPress-1>", self._start_drag)
        date_lbl.bind("<B1-Motion>", self._do_drag)

        # Window controls (right side)
        ctrl_f = tk.Frame(titlebar, bg=SURFACE)
        ctrl_f.pack(side="right", padx=8)

        # Minimize
        self._win_btn(ctrl_f, "—", SURFACE3, TEXT_DIM,
                      lambda: self.root.iconify()).pack(side="left", padx=2)
        # Maximize
        self._win_btn(ctrl_f, "⬜", SURFACE3, TEXT_DIM,
                      self._toggle_maximize).pack(side="left", padx=2)
        # Close
        self._win_btn(ctrl_f, "✕", SURFACE3, FAIL,
                      self.root.destroy, hover_bg=_hex_fade(FAIL, 0.2)).pack(side="left", padx=2)

        # ── Main body ─────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=BG)
        body.pack(side="top", fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────────────────────
        sidebar = tk.Frame(body, bg=SURFACE, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Right border
        tk.Frame(sidebar, bg=BORDER, width=1).pack(side="right", fill="y")

        # Logo section
        logo_f = tk.Frame(sidebar, bg=SURFACE, pady=20)
        logo_f.pack(fill="x")

        logo_inner = tk.Frame(logo_f, bg=SURFACE)
        logo_inner.pack()

        dot2 = tk.Canvas(logo_inner, width=32, height=32, bg=SURFACE,
                         highlightthickness=0)
        dot2.pack(side="left", padx=(0, 10))
        dot2.create_oval(2, 2, 30, 30, fill=ACCENT, outline="")
        dot2.create_text(16, 16, text="S", fill="white", font=("Segoe UI", 13, "bold"))

        name_f = tk.Frame(logo_inner, bg=SURFACE)
        name_f.pack(side="left")
        tk.Label(name_f, text="SelfMaster", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(name_f, text="Покращення Себе", bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas", 7)).pack(anchor="w")

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=12, pady=(0, 6))

        # Nav items
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

        # Bottom info
        tk.Frame(sidebar, bg=BORDER, height=1).pack(side="bottom", fill="x", padx=12, pady=(0, 6))
        bottom = tk.Frame(sidebar, bg=SURFACE)
        bottom.pack(side="bottom", fill="x", padx=14, pady=(0, 10))
        tk.Label(bottom, text=f"💾 {DB_PATH}", bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas", 6), wraplength=175, justify="left").pack(anchor="w")

        # Content area
        self._content = tk.Frame(body, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        # Tabs
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

    def _win_btn(self, parent, text, bg, fg, cmd, hover_bg=None):
        """Small window control button."""
        if hover_bg is None:
            hover_bg = SURFACE3
        b = tk.Label(parent, text=text, bg=SURFACE, fg=fg,
                     font=("Segoe UI", 10), cursor="hand2",
                     width=3, pady=4)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.configure(bg=SURFACE))
        return b

    def _make_nav_btn(self, parent, emoji, label, key, color):
        f = tk.Frame(parent, bg=SURFACE, cursor="hand2")
        f.pack(fill="x", padx=8, pady=1)

        indicator = tk.Frame(f, bg=SURFACE, width=3)
        indicator.pack(side="left", fill="y")

        inner = tk.Frame(f, bg=SURFACE, padx=10, pady=10)
        inner.pack(side="left", fill="x", expand=True)

        em_lbl = tk.Label(inner, text=emoji, bg=SURFACE, font=("Segoe UI", 12))
        em_lbl.pack(side="left", padx=(0, 8))

        txt_lbl = tk.Label(inner, text=label, bg=SURFACE, fg=TEXT_DIM,
                           font=("Segoe UI", 9, "bold"), anchor="w")
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
            w.configure(bg=_hex_fade(color, 0.08))
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