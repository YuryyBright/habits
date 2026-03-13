"""SelfMaster — Month Grid Tab"""
import tkinter as tk
from tkinter import ttk
from datetime import date
import calendar
from ui import *
from ui.theme import *
from ui.widgets import scrollable_frame, hscrollable_frame, card, section_header, _hex_fade
from db import queries as db


class MonthTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        today = date.today()
        self._year = today.year
        self._month = today.month
        self._build()

    def _build(self):
        # Nav bar
        nav = tk.Frame(self, bg=SURFACE, padx=24, pady=14)
        nav.pack(fill="x")
        tk.Frame(nav, bg=BORDER, height=1).pack(fill="x", side="bottom")

        btn_prev = tk.Label(nav, text="‹", bg=SURFACE2, fg=TEXT_MID,
                            font=("Segoe UI",16,"bold"), cursor="hand2", width=3)
        btn_prev.pack(side="left")
        btn_prev.bind("<Button-1>", lambda e: self._change_month(-1))
        btn_prev.bind("<Enter>", lambda e: btn_prev.configure(bg=SURFACE3, fg=TEXT))
        btn_prev.bind("<Leave>", lambda e: btn_prev.configure(bg=SURFACE2, fg=TEXT_MID))

        self._month_var = tk.StringVar()
        tk.Label(nav, textvariable=self._month_var, bg=SURFACE, fg=TEXT,
                 font=("Segoe UI",14,"bold")).pack(side="left", padx=16)

        btn_next = tk.Label(nav, text="›", bg=SURFACE2, fg=TEXT_MID,
                            font=("Segoe UI",16,"bold"), cursor="hand2", width=3)
        btn_next.pack(side="left")
        btn_next.bind("<Button-1>", lambda e: self._change_month(1))
        btn_next.bind("<Enter>", lambda e: btn_next.configure(bg=SURFACE3, fg=TEXT))
        btn_next.bind("<Leave>", lambda e: btn_next.configure(bg=SURFACE2, fg=TEXT_MID))

        self._stats_frame = tk.Frame(self, bg=BG, padx=20, pady=8)
        self._stats_frame.pack(fill="x")

        outer, self._grid_inner = hscrollable_frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=4)

        # Heatmap
        self._heatmap_frame = tk.Frame(self, bg=SURFACE, padx=20, pady=12)
        self._heatmap_frame.pack(fill="x", padx=20, pady=(4,16))
        tk.Frame(self._heatmap_frame, bg=ACCENT, height=2).pack(fill="x")
        tk.Label(self._heatmap_frame, text="ТЕПЛОВА КАРТА", bg=SURFACE,
                 fg=TEXT_DIM, font=("Consolas",8,"bold")).pack(anchor="w", pady=(6,4))
        self._heatmap_cells = tk.Frame(self._heatmap_frame, bg=SURFACE)
        self._heatmap_cells.pack(fill="x")

        self.refresh()

    def refresh(self):
        MONTHS = ["Січень","Лютий","Березень","Квітень","Травень","Червень",
                  "Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"]
        self._month_var.set(f"{MONTHS[self._month-1]}  {self._year}")

        days = calendar.monthrange(self._year, self._month)[1]
        today = date.today()
        is_cur = (today.year == self._year and today.month == self._month)
        today_day = today.day if is_cur else -1

        habits = db.get_habits()
        logs = db.get_logs_for_month(self._year, self._month)

        self._build_stats(habits, logs, days, today_day)
        self._build_grid(habits, logs, days, today_day)
        self._build_heatmap(habits, logs, days, today_day)

    def _build_stats(self, habits, logs, days, today_day):
        for w in self._stats_frame.winfo_children():
            w.destroy()

        passed = today_day if today_day > 0 else days
        done_slots = total_slots = 0
        for h in habits:
            hlog = logs.get(h['id'], {})
            for d in range(1, passed+1):
                val = hlog.get(d)
                if val is not None:
                    total_slots += 1
                    if self._is_done(val, h): done_slots += 1

        pct = round(done_slots/total_slots*100) if total_slots else 0

        for label, val, sub, color in [
            ("Виконано", f"{done_slots}", f"з {total_slots}", ACCENT),
            ("% виконання", f"{pct}%", "загальний", ACCENT3),
            ("Звичок", str(len(habits)), "активних", ACCENT2),
            ("Днів пройшло", str(passed), f"з {days}", STREAK),
        ]:
            f = tk.Frame(self._stats_frame, bg=SURFACE, padx=14, pady=10)
            f.pack(side="left", padx=(0,8))
            tk.Frame(f, bg=color, height=2).pack(fill="x")
            tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",8)).pack(anchor="w", pady=(4,0))
            tk.Label(f, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI",20,"bold")).pack(anchor="w")
            tk.Label(f, text=sub, bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",8)).pack(anchor="w")

    def _build_grid(self, habits, logs, days, today_day):
        for w in self._grid_inner.winfo_children():
            w.destroy()
        if not habits:
            tk.Label(self._grid_inner, text="Немає звичок",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=20)
            return

        # Header
        hdr = tk.Frame(self._grid_inner, bg=SURFACE2)
        hdr.pack(fill="x")
        tk.Label(hdr, text="ЗВИЧКА", bg=SURFACE2, fg=TEXT_DIM,
                 font=("Consolas",8), width=22, anchor="w").pack(side="left", padx=12)

        for d in range(1, days+1):
            is_today = d == today_day
            bg = SURFACE3 if is_today else SURFACE2
            fg = ACCENT_L if is_today else TEXT_DIM
            tk.Label(hdr, text=str(d), bg=bg, fg=fg,
                     font=("Consolas",8), width=3, anchor="center").pack(side="left")

        for lbl in ["Вик.", "%", "🔥"]:
            tk.Label(hdr, text=lbl, bg=SURFACE2, fg=ACCENT3,
                     font=("Consolas",8), width=5).pack(side="left")

        # Rows
        for i, h in enumerate(habits):
            hid = h['id']
            hlog = logs.get(hid, {})
            row_bg = SURFACE if i%2==0 else SURFACE2
            row = tk.Frame(self._grid_inner, bg=row_bg)
            row.pack(fill="x")

            # Color dot + label
            habit_color = h.get('color', ACCENT)
            dot_f = tk.Frame(row, bg=row_bg, width=180)
            dot_f.pack_propagate(False)
            dot_f.pack(side="left")
            inner = tk.Frame(dot_f, bg=row_bg)
            inner.pack(side="left", fill="y", pady=4)
            tk.Frame(inner, bg=habit_color, width=2, height=24).pack(side="left", padx=(8,8), pady=5)
            tk.Label(inner, text=f"{h['emoji']} {h['name']}", bg=row_bg,
                     fg=TEXT, font=FONT_MONO, anchor="w").pack(side="left")

            done_cnt = logged_cnt = 0
            for d in range(1, days+1):
                val = hlog.get(d)
                is_future = d > today_day > 0
                is_today_cell = d == today_day
                cell_t, cell_fg, cell_bg = self._cell_display(val, h, is_future, is_today_cell, row_bg)

                cell = tk.Label(row, text=cell_t, bg=cell_bg, fg=cell_fg,
                                font=("Consolas",9), width=3, cursor="hand2" if not is_future else "arrow",
                                relief="flat", anchor="center")
                cell.pack(side="left", pady=2, padx=1)

                if not is_future and val is not None:
                    logged_cnt += 1
                    if self._is_done(val, h): done_cnt += 1

                if not is_future:
                    cell.bind("<Button-1>", lambda e, hid=hid, d=d: self._toggle_cell(hid, d))

            pct = round(done_cnt/logged_cnt*100) if logged_cnt else 0
            cur_s, _ = db.get_habit_streak(hid)

            tk.Label(row, text=str(done_cnt), bg=row_bg, fg=ACCENT,
                     font=("Consolas",9,"bold"), width=5).pack(side="left")
            pct_c = DONE if pct>=70 else STREAK if pct>=40 else FAIL
            tk.Label(row, text=f"{pct}%" if logged_cnt else "—",
                     bg=row_bg, fg=pct_c, font=("Consolas",9), width=5).pack(side="left")
            tk.Label(row, text=f"🔥{cur_s}" if cur_s>=1 else "—",
                     bg=row_bg, fg=STREAK, font=("Consolas",9), width=5).pack(side="left")

        # Legend
        legend = tk.Frame(self._grid_inner, bg=BG, pady=6)
        legend.pack(fill="x")
        for txt, clr in [("✔ Виконано",DONE),("✖ Пропустив",FAIL),
                          ("# Число",ACCENT3),("· Порожньо",TEXT_DIM)]:
            tk.Label(legend, text=txt, bg=BG, fg=clr, font=FONT_MONO).pack(side="left", padx=12)

    def _cell_display(self, val, habit, is_future, is_today, base_bg):
        if is_future: return "·", BORDER, base_bg
        if val is None: return "·", TEXT_DIM, base_bg
        if val == 'done': return "✔", DONE, _hex_fade(DONE, 0.2)
        if val == 'fail': return "✖", FAIL, _hex_fade(FAIL, 0.15)
        try:
            n = float(val)
            if habit.get('is_negative'):
                clr = DONE if n==0 else (STREAK if n<=5 else FAIL)
            else:
                goal = habit.get('goal_value') or 1
                clr = DONE if n>=goal else (ACCENT3 if n>0 else FAIL)
            display = str(int(n)) if n==int(n) else str(n)
            return display[:3], clr, _hex_fade(clr, 0.15)
        except:
            return str(val)[:3], ACCENT3, _hex_fade(ACCENT3, 0.15)

    def _is_done(self, val, habit):
        if val == 'done': return True
        if val == 'fail': return False
        try:
            n = float(val)
            return n==0 if habit.get('is_negative') else n>0
        except: return False

    def _toggle_cell(self, habit_id, day):
        log_date = date(self._year, self._month, day)
        habit = db.get_habit_by_id(habit_id)
        logs = db.get_logs_for_month(self._year, self._month)
        val = logs.get(habit_id, {}).get(day)

        if habit['type'] == 'toggle':
            if val is None: db.log_habit(habit_id, log_date, 'done')
            elif val == 'done': db.log_habit(habit_id, log_date, 'fail')
            else: db.clear_log(habit_id, log_date)
        else:
            self._edit_number(habit_id, habit, log_date, val)
        self.refresh()

    def _edit_number(self, habit_id, habit, log_date, current_val):
        win = tk.Toplevel(self)
        win.title(f"{habit['emoji']} {habit['name']}")
        win.configure(bg=SURFACE2)
        win.geometry("280x150")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=f"{habit['emoji']}  {habit['name']}",
                 bg=SURFACE2, fg=TEXT, font=FONT_BOLD).pack(pady=(16,4))
        tk.Label(win, text=f"({habit.get('unit','')})",
                 bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack()

        var = tk.StringVar(value=str(current_val) if current_val else "")
        e = tk.Entry(win, textvariable=var, bg=SURFACE3, fg=TEXT,
                     font=("Consolas",16), insertbackground=TEXT,
                     justify="center", relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER)
        e.pack(padx=20, fill="x", ipady=8, pady=8)
        e.focus_set()

        def confirm(ev=None):
            try:
                n = float(var.get())
                db.log_habit(habit_id, log_date, int(n) if n==int(n) else n)
                win.destroy(); self.refresh()
            except: pass

        def clear():
            db.clear_log(habit_id, log_date)
            win.destroy(); self.refresh()

        e.bind("<Return>", confirm)
        btn_f = tk.Frame(win, bg=SURFACE2)
        btn_f.pack()
        tk.Button(btn_f, text="ОК", command=confirm, bg=ACCENT, fg=TEXT,
                  font=FONT_BOLD, relief="flat", padx=16).pack(side="left", padx=4)
        tk.Button(btn_f, text="Очистити", command=clear,
                  bg=SURFACE3, fg=FAIL, font=FONT_MONO, relief="flat").pack(side="left")

    def _build_heatmap(self, habits, logs, days, today_day):
        for w in self._heatmap_cells.winfo_children():
            w.destroy()

        # Gradient from dark to accent color
        LEVELS = [SURFACE2, _hex_fade(ACCENT,0.2), _hex_fade(ACCENT,0.35),
                  _hex_fade(ACCENT,0.5), _hex_fade(ACCENT,0.7), _hex_fade(ACCENT,0.9)]

        cells = tk.Frame(self._heatmap_cells, bg=SURFACE)
        cells.pack(fill="x")

        for d in range(1, days+1):
            is_future = d > today_day > 0
            pct = 0
            if is_future:
                bg = SURFACE
            else:
                done_cnt = sum(1 for h in habits
                    if logs.get(h['id'],{}).get(d) is not None
                    and self._is_done(logs.get(h['id'],{}).get(d), h))
                logged = sum(1 for h in habits if logs.get(h['id'],{}).get(d) is not None)
                if logged > 0:
                    pct = done_cnt / logged
                    bg = LEVELS[min(5, int(pct*5.99))]
                else:
                    bg = SURFACE2

            is_today = (d == today_day)
            fg = TEXT if pct >= 0.5 else TEXT_DIM
            if is_today: fg = ACCENT_L

            cell = tk.Label(cells, text=str(d), bg=bg, fg=fg,
                            font=("Consolas",8), width=3, height=2)
            cell.pack(side="left", padx=1, pady=1)
            if is_today:
                cell.configure(highlightthickness=1, highlightbackground=ACCENT_L)

    def _change_month(self, delta):
        self._month += delta
        if self._month > 12: self._month = 1; self._year += 1
        if self._month < 1: self._month = 12; self._year -= 1
        self.refresh()
