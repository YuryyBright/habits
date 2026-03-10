"""
SelfMaster - Monthly Tracker Tab
Full-month habit grid view with heatmap.
"""
import tkinter as tk
from tkinter import ttk
from datetime import date
import calendar
from .theme import *
from .widgets import *
from db import queries as Q


class MonthTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        today = date.today()
        self._year = today.year
        self._month = today.month
        self._build()

    def _build(self):
        # Navigation
        nav = tk.Frame(self, bg=BG)
        nav.pack(fill="x", padx=20, pady=(16, 8))

        tk.Button(nav, text="‹", bg=SURFACE2, fg=TEXT,
                  font=("Segoe UI", 14), relief="flat", cursor="hand2",
                  command=lambda: self._change_month(-1)).pack(side="left")

        self._month_var = tk.StringVar()
        tk.Label(nav, textvariable=self._month_var, bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=16)

        tk.Button(nav, text="›", bg=SURFACE2, fg=TEXT,
                  font=("Segoe UI", 14), relief="flat", cursor="hand2",
                  command=lambda: self._change_month(1)).pack(side="left")

        # Stats strip
        self._stats_frame = tk.Frame(self, bg=BG)
        self._stats_frame.pack(fill="x", padx=20, pady=(0, 8))

        # Grid area (horizontal scroll)
        outer, self._grid_inner = hscrollable_frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=4)

        # Heatmap
        self._heatmap_frame = tk.Frame(self, bg=SURFACE, padx=14, pady=10)
        self._heatmap_frame.pack(fill="x", padx=20, pady=4)
        tk.Frame(self._heatmap_frame, bg=ACCENT, height=2).pack(fill="x")
        tk.Label(self._heatmap_frame, text="ТЕПЛОВА КАРТА ПРОГРЕСУ",
                 bg=SURFACE, fg=TEXT_DIM, font=("Consolas", 9)).pack(anchor="w", pady=(6, 6))
        self._heatmap_cells_frame = tk.Frame(self._heatmap_frame, bg=SURFACE)
        self._heatmap_cells_frame.pack(fill="x")

        self.refresh()

    def refresh(self):
        months = ["Січень","Лютий","Березень","Квітень","Травень","Червень",
                  "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
        self._month_var.set(f"{months[self._month-1]} {self._year}")

        days = calendar.monthrange(self._year, self._month)[1]
        today = date.today()
        is_cur = (today.year == self._year and today.month == self._month)
        today_day = today.day if is_cur else -1

        habits = Q.get_habits()
        logs = Q.get_logs_for_month(self._year, self._month)

        self._build_stats(habits, logs, days, today_day)
        self._build_grid(habits, logs, days, today_day)
        self._build_heatmap(habits, logs, days, today_day)

    def _build_stats(self, habits, logs, days, today_day):
        for w in self._stats_frame.winfo_children():
            w.destroy()

        passed = today_day if today_day > 0 else days
        total_slots = 0
        done_slots = 0
        for h in habits:
            hlog = logs.get(h['id'], {})
            for d in range(1, passed + 1):
                val = hlog.get(d)
                if val is not None:
                    total_slots += 1
                    if self._is_done(val, h):
                        done_slots += 1

        pct = round(done_slots / total_slots * 100) if total_slots else 0

        stats = [
            ("Виконано", f"{done_slots}", f"з {total_slots}", ACCENT),
            ("% виконання", f"{pct}%", "загальний", ACCENT2),
            ("Звичок", str(len(habits)), "активних", ACCENT3),
            ("Днів пройшло", str(passed), f"з {days}", STREAK),
        ]
        for label, val, sub, color in stats:
            f = tk.Frame(self._stats_frame, bg=SURFACE, padx=14, pady=10)
            f.pack(side="left", padx=(0, 8))
            tk.Frame(f, bg=color, height=2).pack(fill="x")
            tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 8)).pack(anchor="w", pady=(4, 0))
            tk.Label(f, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI", 22, "bold")).pack(anchor="w")
            tk.Label(f, text=sub, bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 8)).pack(anchor="w")

    def _build_grid(self, habits, logs, days, today_day):
        for w in self._grid_inner.winfo_children():
            w.destroy()

        if not habits:
            tk.Label(self._grid_inner, text="Немає звичок",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=20)
            return

        CELL_W = 34
        HABIT_COL_W = 180
        today = date.today()

        # Header row
        hdr = tk.Frame(self._grid_inner, bg=SURFACE2)
        hdr.pack(fill="x")

        tk.Label(hdr, text="ЗВИЧКА", bg=SURFACE2, fg=TEXT_DIM,
                 font=("Consolas", 9), width=22, anchor="w").pack(side="left", padx=12)

        for d in range(1, days + 1):
            bg = SURFACE2 if d != today_day else BG
            fg = ACCENT if d == today_day else TEXT_DIM
            tk.Label(hdr, text=str(d), bg=bg, fg=fg,
                     font=("Consolas", 8), width=3, anchor="center").pack(side="left")

        for lbl in ["Вик.", "%", "🔥"]:
            tk.Label(hdr, text=lbl, bg=SURFACE2, fg=ACCENT3,
                     font=("Consolas", 8), width=5).pack(side="left")

        # Habit rows
        for i, h in enumerate(habits):
            hid = h['id']
            hlog = logs.get(hid, {})
            row_bg = SURFACE if i % 2 == 0 else SURFACE2

            row = tk.Frame(self._grid_inner, bg=row_bg)
            row.pack(fill="x")

            # Label
            lbl_frame = tk.Frame(row, bg=row_bg, width=HABIT_COL_W)
            lbl_frame.pack_propagate(False)
            lbl_frame.pack(side="left")
            tk.Label(lbl_frame, text=f"{h['emoji']} {h['name']}",
                     bg=row_bg, fg=TEXT, font=FONT_MAIN, anchor="w").pack(
                side="left", padx=12, pady=6)

            done_cnt = 0
            logged_cnt = 0
            for d in range(1, days + 1):
                val = hlog.get(d)
                is_future = d > today_day and today_day > 0
                is_today = d == today_day
                cell_bg = row_bg if not is_today else BG

                if val is not None and not is_future:
                    logged_cnt += 1
                    if self._is_done(val, h):
                        done_cnt += 1

                # Cell button
                cell_text, cell_fg, cell_bg2 = self._cell_display(val, h, is_future, is_today, row_bg)

                cell = tk.Label(row, text=cell_text, bg=cell_bg2,
                                fg=cell_fg, font=("Consolas", 9), width=3,
                                cursor="hand2" if not is_future else "arrow",
                                relief="flat", anchor="center")
                cell.pack(side="left", pady=2, padx=1)

                if not is_future:
                    cell.bind("<Button-1>",
                              lambda e, hid=hid, d=d: self._toggle_cell(hid, d))

            # Stats
            pct = round(done_cnt / logged_cnt * 100) if logged_cnt else 0
            cur_s, _ = Q.get_habit_streak(hid)

            tk.Label(row, text=str(done_cnt), bg=row_bg, fg=ACCENT,
                     font=("Consolas", 9, "bold"), width=5).pack(side="left")
            pct_color = DONE if pct >= 70 else STREAK if pct >= 40 else FAIL
            tk.Label(row, text=f"{pct}%" if logged_cnt else "—",
                     bg=row_bg, fg=pct_color,
                     font=("Consolas", 9), width=5).pack(side="left")
            tk.Label(row, text=f"🔥{cur_s}" if cur_s >= 1 else "—",
                     bg=row_bg, fg=STREAK,
                     font=("Consolas", 9), width=5).pack(side="left")

        # Legend
        legend = tk.Frame(self._grid_inner, bg=BG, pady=8)
        legend.pack(fill="x")
        items = [("✔ Виконано", DONE), ("✖ Не виконано", FAIL), ("# Число", ACCENT3), ("· Порожньо", TEXT_DIM)]
        for txt, clr in items:
            tk.Label(legend, text=txt, bg=BG, fg=clr, font=FONT_MONO).pack(side="left", padx=12)

    def _cell_display(self, val, habit, is_future, is_today, base_bg):
        """Returns (text, fg, bg) for a cell."""
        if is_future:
            return "·", BORDER, base_bg
        if val is None:
            return "·", TEXT_DIM, base_bg
        if val == 'done':
            return "✔", DONE, DONE + "22"
        if val == 'fail':
            return "✖", FAIL, FAIL + "22"
        try:
            n = float(val)
            if habit.get('is_negative'):
                clr = DONE if n == 0 else (STREAK if n <= 5 else FAIL)
            else:
                goal = habit.get('goal_value') or 1
                clr = DONE if n >= goal else (ACCENT3 if n > 0 else FAIL)
            display = str(int(n)) if n == int(n) else str(n)
            return display[:3], clr, clr + "22"
        except:
            return str(val)[:3], ACCENT3, ACCENT3 + "22"

    def _is_done(self, val, habit):
        if val == 'done':
            return True
        if val == 'fail':
            return False
        try:
            n = float(val)
            return n == 0 if habit.get('is_negative') else n > 0
        except:
            return False

    def _toggle_cell(self, habit_id, day):
        log_date = date(self._year, self._month, day)
        habit = Q.get_habit_by_id(habit_id)
        logs = Q.get_logs_for_month(self._year, self._month)
        val = logs.get(habit_id, {}).get(day)

        if habit['type'] == 'toggle':
            if val is None:
                Q.log_habit(habit_id, log_date, 'done')
            elif val == 'done':
                Q.log_habit(habit_id, log_date, 'fail')
            else:
                Q.clear_log(habit_id, log_date)
        else:
            self._edit_number(habit_id, habit, log_date, val)

        self.refresh()

    def _edit_number(self, habit_id, habit, log_date, current_val):
        win = tk.Toplevel()
        win.title(f"{habit['emoji']} {habit['name']}")
        win.configure(bg=SURFACE2)
        win.geometry("260x140")
        win.resizable(False, False)

        tk.Label(win, text=f"{habit['emoji']} {habit['name']}",
                 bg=SURFACE2, fg=TEXT, font=FONT_BOLD).pack(pady=(16, 4))
        tk.Label(win, text=f"Введіть значення ({habit.get('unit', '')}):",
                 bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack()

        var = tk.StringVar(value=str(current_val) if current_val else "")
        e = tk.Entry(win, textvariable=var, bg=SURFACE, fg=TEXT,
                     font=("Consolas", 14), insertbackground=TEXT,
                     justify="center", relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT3,
                     highlightbackground=BORDER)
        e.pack(padx=20, fill="x", ipady=6)
        e.focus_set()

        def confirm(ev=None):
            try:
                n = float(var.get())
                Q.log_habit(habit_id, log_date, int(n) if n == int(n) else n)
                win.destroy()
                self.refresh()
            except:
                pass

        def clear_val():
            Q.clear_log(habit_id, log_date)
            win.destroy()
            self.refresh()

        e.bind("<Return>", confirm)
        btn_f = tk.Frame(win, bg=SURFACE2)
        btn_f.pack(pady=8)
        tk.Button(btn_f, text="ОК", command=confirm, bg=ACCENT, fg=BG,
                  font=FONT_BOLD, relief="flat", padx=16).pack(side="left", padx=4)
        tk.Button(btn_f, text="Очистити", command=clear_val,
                  bg=SURFACE, fg=FAIL, font=FONT_MONO, relief="flat").pack(side="left")

    def _build_heatmap(self, habits, logs, days, today_day):
        for w in self._heatmap_cells_frame.winfo_children():
            w.destroy()

        cells = tk.Frame(self._heatmap_cells_frame, bg=SURFACE)
        cells.pack(fill="x")

        for d in range(1, days + 1):
            is_future = d > today_day > 0
            if is_future:
                bg = SURFACE2
            else:
                done_cnt = sum(
                    1 for h in habits
                    if self._is_done(logs.get(h['id'], {}).get(d), h)
                       and logs.get(h['id'], {}).get(d) is not None
                )
                logged = sum(1 for h in habits if logs.get(h['id'], {}).get(d) is not None)
                pct = done_cnt / logged if logged > 0 else 0
                if pct == 0 and logged == 0:
                    bg = SURFACE2
                elif pct >= 1.0:
                    bg = ACCENT
                elif pct >= 0.8:
                    bg = ACCENT + "cc"
                elif pct >= 0.6:
                    bg = ACCENT + "99"
                elif pct >= 0.4:
                    bg = ACCENT + "66"
                elif pct >= 0.2:
                    bg = ACCENT + "33"
                else:
                    bg = FAIL + "44"

            cell = tk.Label(cells, text=str(d), bg=bg,
                            fg=BG if pct >= 0.8 else TEXT_DIM,
                            font=("Consolas", 8), width=3, height=2)
            cell.pack(side="left", padx=1, pady=1)

    def _change_month(self, delta):
        self._month += delta
        if self._month > 12:
            self._month = 1
            self._year += 1
        if self._month < 1:
            self._month = 12
            self._year -= 1
        self.refresh()
