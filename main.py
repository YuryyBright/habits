"""
SelfMaster — Інструмент для покращення себе
Головний файл запуску.

Вкладки:
  1. Сьогодні   — щоденне логування звичок + щоденник + ідеальна людина
  2. Місяць     — повна таблиця-сітка за місяць
  3. Статистика — графіки та аналітика
  4. Ідеал      — критерії ідеальної людини
  5. Звички     — керування звичками
  6. Цілі       — постановка та відстеження цілей
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import init_db
from ui.theme import apply_theme, BG, SURFACE, SURFACE2, TEXT, ACCENT, TEXT_DIM, BORDER
from ui import TodayTab, MonthTab, StatsTab, IdealTab, HabitsTab, GoalsTab


class SelfMasterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SelfMaster — Покращення Себе")
        self.root.geometry("1280x820")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        # Icon (optional)
        try:
            # If bundled with PyInstaller
            base = sys._MEIPASS
        except AttributeError:
            base = os.path.dirname(os.path.abspath(__file__))

        # Init DB
        init_db()

        # Apply theme
        apply_theme(self.root)

        self._build_ui()
        self._auto_refresh()

    def _build_ui(self):
        # ── Sidebar nav ───────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=SURFACE, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(sidebar, bg=SURFACE, pady=20)
        logo.pack(fill="x")
        tk.Label(logo, text="SELF", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack()
        tk.Label(logo, text="MASTER", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack()
        tk.Label(logo, text="Покращення Себе", bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas", 8)).pack()

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16)

        # Navigation items
        nav_items = [
            ("📅", "Сьогодні",   "today"),
            ("📊", "Місяць",     "month"),
            ("📈", "Статистика", "stats"),
            ("🌟", "Ідеал",      "ideal"),
            ("⚙️", "Звички",     "habits"),
            ("🎯", "Цілі",       "goals"),
        ]

        self._nav_btns = {}
        self._active_tab = tk.StringVar(value="today")

        for emoji, label, key in nav_items:
            btn = self._nav_button(sidebar, emoji, label, key)
            self._nav_btns[key] = btn

        # Bottom: date + version
        bottom = tk.Frame(sidebar, bg=SURFACE)
        bottom.pack(side="bottom", fill="x", padx=12, pady=12)
        from datetime import date
        tk.Label(bottom, text=date.today().strftime("%d.%m.%Y"),
                 bg=SURFACE, fg=TEXT_DIM, font=("Consolas", 9)).pack(anchor="w")
        tk.Label(bottom, text="v1.0.0", bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas", 8)).pack(anchor="w")

        # ── Content area ─────────────────────────────────────────────────
        self._content = tk.Frame(self.root, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        # ── Tab frames ────────────────────────────────────────────────────
        self._tabs = {}
        tab_classes = {
            "today":  TodayTab,
            "month":  MonthTab,
            "stats":  StatsTab,
            "ideal":  IdealTab,
            "habits": HabitsTab,
            "goals":  GoalsTab,
        }
        for key, cls in tab_classes.items():
            tab = cls(self._content)
            tab.place(relwidth=1, relheight=1)
            self._tabs[key] = tab

        self._switch_tab("today")

    def _nav_button(self, parent, emoji, label, key):
        f = tk.Frame(parent, bg=SURFACE, cursor="hand2")
        f.pack(fill="x", padx=8, pady=2)

        inner = tk.Frame(f, bg=SURFACE, padx=12, pady=10)
        inner.pack(fill="x")

        em_lbl = tk.Label(inner, text=emoji, bg=SURFACE,
                          font=("Segoe UI", 14))
        em_lbl.pack(side="left", padx=(0, 10))

        txt_lbl = tk.Label(inner, text=label, bg=SURFACE, fg=TEXT_DIM,
                           font=("Segoe UI", 10, "bold"), anchor="w")
        txt_lbl.pack(side="left", fill="x", expand=True)

        accent_bar = tk.Frame(f, bg=SURFACE, width=3)
        accent_bar.pack(side="right", fill="y")

        def on_enter(e):
            if self._active_tab.get() != key:
                inner.configure(bg=SURFACE2)
                em_lbl.configure(bg=SURFACE2)
                txt_lbl.configure(bg=SURFACE2)
                f.configure(bg=SURFACE2)

        def on_leave(e):
            if self._active_tab.get() != key:
                inner.configure(bg=SURFACE)
                em_lbl.configure(bg=SURFACE)
                txt_lbl.configure(bg=SURFACE)
                f.configure(bg=SURFACE)

        def on_click(e):
            self._switch_tab(key)

        for w in [f, inner, em_lbl, txt_lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        f._inner = inner
        f._em = em_lbl
        f._txt = txt_lbl
        f._bar = accent_bar
        return f

    def _switch_tab(self, key):
        # Deactivate old
        old = self._active_tab.get()
        if old in self._nav_btns:
            btn = self._nav_btns[old]
            for w in [btn, btn._inner, btn._em, btn._txt]:
                w.configure(bg=SURFACE)
            btn._txt.configure(fg=TEXT_DIM)
            btn._bar.configure(bg=SURFACE)

        # Activate new
        self._active_tab.set(key)
        btn = self._nav_btns[key]
        for w in [btn, btn._inner, btn._em, btn._txt]:
            w.configure(bg=BG)
        btn._txt.configure(fg=ACCENT)
        btn._bar.configure(bg=ACCENT)

        # Show tab
        for k, tab in self._tabs.items():
            if k == key:
                tab.lift()
            else:
                tab.lower()

        # Refresh the active tab
        if hasattr(self._tabs[key], 'refresh'):
            self._tabs[key].refresh()

    def _auto_refresh(self):
        """Auto-refresh every 60 seconds."""
        active = self._active_tab.get()
        if hasattr(self._tabs.get(active), 'refresh'):
            pass  # only refresh on switch to avoid interrupting editing
        self.root.after(60000, self._auto_refresh)

    def run(self):
        self.root.mainloop()


def main():
    app = SelfMasterApp()
    app.run()


if __name__ == "__main__":
    main()
