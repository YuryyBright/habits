"""SelfMaster — Today Tab"""
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from ui import *
from ui.theme import *
from ui.widgets import (
    _hex_fade, 
    scrollable_frame, 
    MoodPicker, 
    ScoreSlider, 
    card, 
    section_header
)
from db import queries as db
from config import WEEKDAYS_UK, MONTHS_UK_GEN


class TodayTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._selected_date = date.today()
        self._ideal_widgets = {}
        self._build()

    def _build(self):
        # ── Top nav bar ──────────────────────────────────────────────────
        nav = tk.Frame(self, bg=SURFACE, pady=0)
        nav.pack(fill="x")
        tk.Frame(nav, bg=BORDER, height=1).pack(fill="x", side="bottom")

        inner_nav = tk.Frame(nav, bg=SURFACE, padx=24, pady=14)
        inner_nav.pack(fill="x")

        # Date nav
        date_frame = tk.Frame(inner_nav, bg=SURFACE)
        date_frame.pack(side="left")

        btn_prev = tk.Label(date_frame, text="‹", bg=SURFACE2, fg=TEXT_MID,
                            font=("Segoe UI", 16, "bold"), cursor="hand2",
                            width=3, relief="flat")
        btn_prev.pack(side="left", padx=(0,4))
        btn_prev.bind("<Button-1>", lambda e: self._prev_day())
        btn_prev.bind("<Enter>", lambda e: btn_prev.configure(bg=SURFACE3, fg=TEXT))
        btn_prev.bind("<Leave>", lambda e: btn_prev.configure(bg=SURFACE2, fg=TEXT_MID))

        self._date_var = tk.StringVar()
        tk.Label(date_frame, textvariable=self._date_var, bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=12)

        btn_next = tk.Label(date_frame, text="›", bg=SURFACE2, fg=TEXT_MID,
                            font=("Segoe UI", 16, "bold"), cursor="hand2",
                            width=3, relief="flat")
        btn_next.pack(side="left", padx=(4,16))
        btn_next.bind("<Button-1>", lambda e: self._next_day())
        btn_next.bind("<Enter>", lambda e: btn_next.configure(bg=SURFACE3, fg=TEXT))
        btn_next.bind("<Leave>", lambda e: btn_next.configure(bg=SURFACE2, fg=TEXT_MID))

        today_btn = tk.Label(inner_nav, text="● Сьогодні", bg=_hex_fade(ACCENT, 0.15),
                             fg=ACCENT_L, font=FONT_MONO, cursor="hand2",
                             padx=8, pady=4)
        today_btn.pack(side="left")
        today_btn.bind("<Button-1>", lambda e: self._go_today())

        # Mood/energy (right)
        mood_right = tk.Frame(inner_nav, bg=SURFACE)
        mood_right.pack(side="right")

        self._mood_frame = tk.Frame(mood_right, bg=SURFACE)
        self._mood_frame.pack()
        self._build_mood_row()

        # ── Scroll area ──────────────────────────────────────────────────
        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=0, pady=0)

        self.refresh()

    def _build_mood_row(self):
        for w in self._mood_frame.winfo_children():
            w.destroy()

        tk.Label(self._mood_frame, text="Настрій", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_MONO).pack(side="left", padx=(0,6))
        self._mood_picker = MoodPicker(self._mood_frame, initial=3,
                                        callback=self._save_journal_meta, bg=SURFACE)
        self._mood_picker.pack(side="left")

        tk.Label(self._mood_frame, text="  Енергія", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_MONO).pack(side="left", padx=(8,6))
        self._energy_picker = MoodPicker(self._mood_frame, initial=3,
                                          callback=self._save_journal_meta, bg=SURFACE)
        self._energy_picker.pack(side="left")

    def refresh(self):
        d = self._selected_date
        is_today = (d == date.today())
        label = f"{WEEKDAYS_UK[d.weekday()]}, {d.day} {MONTHS_UK_GEN[d.month-1]} {d.year}"
        if is_today: label += "  •  Сьогодні"
        self._date_var.set(label)

        j = db.get_journal(d)
        if j:
            self._mood_picker.set(j.get('mood', 3))
            self._energy_picker.set(j.get('energy', 3))
        else:
            self._mood_picker.set(3)
            self._energy_picker.set(3)

        for w in self._scroll.winfo_children():
            w.destroy()
        self._ideal_widgets.clear()

        self._build_habits_section()
        self._build_ideal_section()
        self._build_journal_section()

    def _build_habits_section(self):
        parent = self._scroll
        d = self._selected_date
        habits = db.get_habits()
        logs = db.get_logs_for_month(d.year, d.month)
        is_future = d > date.today()

        section_header(parent, "ЗВИЧКИ НА СЬОГОДНІ", ACCENT)

        if not habits:
            c = card(parent, ACCENT)
            c.pack(fill="x", padx=20, pady=(0,12))
            tk.Label(c, text="Немає звичок. Додайте їх у вкладці 'Звички'.",
                     bg=SURFACE, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=8)
            return

        # Group by done/undone for visual ordering
        c = tk.Frame(parent, bg=SURFACE, padx=0, pady=0)
        c.pack(fill="x", padx=20, pady=(0,12))
        tk.Frame(c, bg=ACCENT, height=2).pack(fill="x")

        for i, h in enumerate(habits):
            hid = h['id']
            val = logs.get(hid, {}).get(d.day)
            is_done = self._is_done(val, h)

            row_bg = SURFACE if i % 2 == 0 else SURFACE2
            row = tk.Frame(c, bg=row_bg, padx=16, pady=10)
            row.pack(fill="x")
            row.bind("<Enter>", lambda e, r=row: r.configure(bg=SURFACE3))
            row.bind("<Leave>", lambda e, r=row, bg=row_bg: r.configure(bg=bg))

            # Color accent dot
            habit_color = h.get('color', ACCENT)
            dot = tk.Frame(row, bg=habit_color if is_done else BORDER, width=3, height=28)
            dot.pack(side="left", padx=(0,12))
            dot.pack_propagate(False)

            # Emoji
            tk.Label(row, text=h['emoji'], bg=row_bg,
                     font=("Segoe UI", 15)).pack(side="left", padx=(0,8))

            # Name + meta
            info = tk.Frame(row, bg=row_bg)
            info.pack(side="left", fill="x", expand=True)

            name_clr = TEXT if not is_done else TEXT_MID
            tk.Label(info, text=h['name'], bg=row_bg, fg=name_clr,
                     font=FONT_BOLD, anchor="w").pack(anchor="w")

            meta_parts = []
            if h.get('unit'): meta_parts.append(h['unit'])
            if h.get('goal_value'): meta_parts.append(f"ціль: {int(h['goal_value']) if h['goal_value']==int(h['goal_value']) else h['goal_value']}")
            cur_s, _ = db.get_habit_streak(hid)
            if cur_s >= 2: meta_parts.append(f"🔥 {cur_s} дні поспіль")
            if meta_parts:
                tk.Label(info, text="  ·  ".join(meta_parts), bg=row_bg,
                         fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

            # Controls (right)
            btn_f = tk.Frame(row, bg=row_bg)
            btn_f.pack(side="right")
            self._build_controls(btn_f, h, val, d, is_future, row_bg)

    def _is_done(self, val, h):
        if val is None or val == 'fail': return False
        if val == 'done': return True
        try:
            n = float(val)
            return n == 0 if h.get('is_negative') else n > 0
        except: return False

    def _build_controls(self, parent, habit, val, log_date, is_future, row_bg):
        hid = habit['id']
        htype = habit['type']

        if is_future:
            tk.Label(parent, text="майбутнє", bg=row_bg, fg=BORDER, font=FONT_MONO).pack()
            return

        def _set(v):
            if v is None: db.clear_log(hid, log_date)
            else: db.log_habit(hid, log_date, v)
            self.refresh()

        if htype == 'toggle':
            is_done = val == 'done'
            is_fail = val == 'fail'
            not_set = val is None

            # ✔ button
            done_bg = _hex_fade(DONE, 0.2) if is_done else SURFACE2
            done_fg = DONE if is_done else TEXT_DIM
            done_lbl = tk.Label(parent, text="✔  Виконано", bg=done_bg, fg=done_fg,
                                font=FONT_MONO, cursor="hand2", padx=10, pady=4)
            done_lbl.pack(side="right", padx=(4,0))
            done_lbl.bind("<Button-1>",
                          lambda e: _set('done') if val != 'done' else _set(None))
            done_lbl.bind("<Enter>", lambda e: done_lbl.configure(bg=_hex_fade(DONE, 0.3)))
            done_lbl.bind("<Leave>", lambda e: done_lbl.configure(bg=done_bg))

            # ✖ button
            fail_bg = _hex_fade(FAIL, 0.2) if is_fail else SURFACE2
            fail_fg = FAIL if is_fail else TEXT_DIM
            fail_lbl = tk.Label(parent, text="✖  Пропустив", bg=fail_bg, fg=fail_fg,
                                font=FONT_MONO, cursor="hand2", padx=10, pady=4)
            fail_lbl.pack(side="right")
            fail_lbl.bind("<Button-1>",
                          lambda e: _set('fail') if val != 'fail' else _set(None))
            fail_lbl.bind("<Enter>", lambda e: fail_lbl.configure(bg=_hex_fade(FAIL, 0.3)))
            fail_lbl.bind("<Leave>", lambda e: fail_lbl.configure(bg=fail_bg))

        else:
            # Number type
            cur_num = None
            if val is not None:
                try: cur_num = float(val)
                except: pass

            goal = habit.get('goal_value')
            if cur_num is not None:
                if habit.get('is_negative'):
                    clr = DONE if cur_num == 0 else (STREAK if cur_num <= 3 else FAIL)
                else:
                    clr = DONE if (goal and cur_num >= goal) else (STREAK if cur_num > 0 else FAIL)
                display = f"{int(cur_num) if cur_num == int(cur_num) else cur_num}"
                if habit.get('unit'): display += f" {habit['unit']}"
                tk.Label(parent, text=display, bg=_hex_fade(clr, 0.2), fg=clr,
                         font=FONT_MONO_B, padx=10, pady=4).pack(side="right", padx=(4,0))

            edit_btn = tk.Label(parent, text="✎ Ввести", bg=SURFACE2, fg=ACCENT3,
                                font=FONT_MONO, cursor="hand2", padx=10, pady=4)
            edit_btn.pack(side="right")
            edit_btn.bind("<Button-1>", lambda e: self._edit_number(habit, log_date, val))
            edit_btn.bind("<Enter>", lambda e: edit_btn.configure(bg=SURFACE3))
            edit_btn.bind("<Leave>", lambda e: edit_btn.configure(bg=SURFACE2))

            if habit.get('is_negative'):
                zero_bg = _hex_fade(DONE, 0.2) if val == '0' else SURFACE2
                zero_fg = DONE if val == '0' else TEXT_DIM
                zero_lbl = tk.Label(parent, text="0 ✔", bg=zero_bg, fg=zero_fg,
                                    font=FONT_MONO, cursor="hand2", padx=8, pady=4)
                zero_lbl.pack(side="right", padx=4)
                zero_lbl.bind("<Button-1>", lambda e: _set(0))

    def _edit_number(self, habit, log_date, current_val):
        win = tk.Toplevel(self)
        win.title(f"Ввести значення")
        win.configure(bg=SURFACE2)
        win.geometry("300x160")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=f"{habit['emoji']}  {habit['name']}",
                 bg=SURFACE2, fg=TEXT, font=FONT_BOLD).pack(pady=(20,4))
        unit_txt = f"({habit['unit']})" if habit.get('unit') else ""
        if habit.get('goal_value'):
            unit_txt += f"  ціль: {habit['goal_value']}"

        tk.Label(win, text=unit_txt, bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack()

        var = tk.StringVar(value=str(current_val) if current_val else "")
        e = tk.Entry(win, textvariable=var, bg=SURFACE3, fg=TEXT,
                     font=("Segoe UI", 16), insertbackground=TEXT,
                     justify="center", relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER)
        e.pack(padx=24, fill="x", ipady=8, pady=8)
        e.focus_set()
        e.select_range(0, 'end')

        def confirm(ev=None):
            try:
                n = float(var.get())
                db.log_habit(habit['id'], log_date, int(n) if n == int(n) else n)
                win.destroy()
                self.refresh()
            except: pass

        def clear():
            db.clear_log(habit['id'], log_date)
            win.destroy()
            self.refresh()

        e.bind("<Return>", confirm)
        btn_f = tk.Frame(win, bg=SURFACE2)
        btn_f.pack()
        tk.Button(btn_f, text="Зберегти", command=confirm,
                  bg=ACCENT, fg=TEXT, font=FONT_BOLD, relief="flat", padx=16).pack(side="left", padx=4)
        tk.Button(btn_f, text="Очистити", command=clear,
                  bg=SURFACE3, fg=FAIL, font=FONT_MONO, relief="flat", padx=8).pack(side="left")

    def _build_ideal_section(self):
        parent = self._scroll
        d = self._selected_date
        section_header(parent, "ІДЕАЛЬНА ЛЮДИНА — ОЦІНКА ДНЯ", ACCENT2)

        criteria = db.get_ideal_criteria()
        scores_today = {s['criterion_id']: s for s in db.get_ideal_scores_for_date(d)}

        if not criteria:
            c = card(parent, ACCENT2)
            c.pack(fill="x", padx=20, pady=(0,12))
            tk.Label(c, text="Додайте критерії у вкладці 'Ідеал'.",
                     bg=SURFACE, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=8)
            return

        from collections import defaultdict
        grouped = defaultdict(list)
        for c_item in criteria:
            grouped[c_item['category']].append(c_item)

        for cat, items in grouped.items():
            cat_color = CATEGORY_COLORS.get(cat, ACCENT3)
            cat_label = CATEGORY_LABELS.get(cat, cat)

            c = tk.Frame(parent, bg=SURFACE)
            c.pack(fill="x", padx=20, pady=(0,6))
            tk.Frame(c, bg=cat_color, height=2).pack(fill="x")

            cat_hdr = tk.Frame(c, bg=SURFACE, padx=16, pady=8)
            cat_hdr.pack(fill="x")
            tk.Label(cat_hdr, text=cat_label, bg=SURFACE, fg=cat_color,
                     font=FONT_BOLD).pack(side="left")

            for i, crit in enumerate(items):
                cid = crit['id']
                score_data = scores_today.get(cid)
                score = score_data['score'] if score_data else 0

                row_bg = SURFACE if i % 2 == 0 else SURFACE2
                row = tk.Frame(c, bg=row_bg, padx=16, pady=8)
                row.pack(fill="x")

                tk.Label(row, text=crit['icon'], bg=row_bg,
                         font=("Segoe UI", 13)).pack(side="left", padx=(0,8))

                info = tk.Frame(row, bg=row_bg)
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=crit['title'], bg=row_bg, fg=TEXT,
                         font=FONT_BOLD).pack(anchor="w")
                if crit.get('description'):
                    tk.Label(info, text=crit['description'], bg=row_bg,
                             fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

                score_frame = tk.Frame(row, bg=row_bg)
                score_frame.pack(side="right")

                slider = ScoreSlider(score_frame, initial=score, bg=row_bg,
                                     callback=lambda v, c_id=cid: self._save_ideal_score(c_id, v))
                for child in slider.winfo_children():
                    child.configure(bg=row_bg)
                slider.pack()

                score_labels = {0:"—", 1:"Слабко", 2:"Нижче норми",
                                3:"Нормально", 4:"Добре", 5:"Відмінно"}
                score_lbl = tk.Label(score_frame, text=score_labels.get(score, ""),
                                     bg=row_bg, fg=cat_color if score > 0 else TEXT_DIM,
                                     font=("Consolas", 8), width=12)
                score_lbl.pack()
                self._ideal_widgets[cid] = (score_lbl, cat_color)

    def _save_ideal_score(self, criterion_id, score):
        db.score_ideal(criterion_id, self._selected_date, score)
        if criterion_id in self._ideal_widgets:
            lbl, clr = self._ideal_widgets[criterion_id]
            labels = {0:"—", 1:"Слабко", 2:"Нижче норми",
                      3:"Нормально", 4:"Добре", 5:"Відмінно"}
            lbl.configure(text=labels.get(score, ""),
                          fg=clr if score > 0 else TEXT_DIM)

    def _build_journal_section(self):
        parent = self._scroll
        d = self._selected_date
        j = db.get_journal(d)
        section_header(parent, "ЩОДЕННИК", ACCENT3)

        c = card(parent, ACCENT3, padx=20, pady=16)
        c.pack(fill="x", padx=20, pady=(0,20))

        fields = [
            ("📝  Нотатки дня", "content", 4),
            ("🏆  Перемоги дня", "wins", 2),
            ("🎯  Плани на завтра", "tomorrow", 2),
        ]
        self._journal_vars = {}
        for label, key, height in fields:
            tk.Label(c, text=label, bg=SURFACE, fg=TEXT_MID,
                     font=FONT_MONO).pack(fill="x", pady=(8,2))
            txt = tk.Text(c, height=height, bg=SURFACE2, fg=TEXT,
                          font=("Segoe UI", 10), relief="flat",
                          insertbackground=TEXT, wrap="word",
                          highlightthickness=1, highlightbackground=BORDER,
                          highlightcolor=ACCENT3, bd=6)
            txt.pack(fill="x", pady=(0,2))
            if j and j.get(key): txt.insert("1.0", j[key])
            self._journal_vars[key] = txt

        # Save button
        def save():
            db.save_journal(d,
                mood=self._mood_picker.get(),
                energy=self._energy_picker.get(),
                content=self._journal_vars['content'].get("1.0","end-1c"),
                wins=self._journal_vars['wins'].get("1.0","end-1c"),
                tomorrow=self._journal_vars['tomorrow'].get("1.0","end-1c"),
            )
            save_btn.configure(text="✔  Збережено!", fg=DONE, bg=_hex_fade(DONE,0.15))
            c.after(2000, lambda: save_btn.configure(text="💾  Зберегти щоденник",
                                                      fg=TEXT_MID, bg=SURFACE3))

        save_btn = tk.Label(c, text="💾  Зберегти щоденник",
                            bg=SURFACE3, fg=TEXT_MID,
                            font=FONT_BOLD, cursor="hand2", padx=16, pady=8)
        save_btn.pack(anchor="e", pady=(12,0))
        save_btn.bind("<Button-1>", lambda e: save())
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.2), fg=ACCENT_L))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=SURFACE3, fg=TEXT_MID))

    def _save_journal_meta(self, _=None):
        j = db.get_journal(self._selected_date)
        db.save_journal(self._selected_date,
            mood=self._mood_picker.get(),
            energy=self._energy_picker.get(),
            content=j['content'] if j else "",
            wins=j['wins'] if j else "",
            tomorrow=j['tomorrow'] if j else "",
        )

    def _prev_day(self): self._selected_date -= timedelta(days=1); self.refresh()
    def _next_day(self):
        if self._selected_date < date.today():
            self._selected_date += timedelta(days=1); self.refresh()
    def _go_today(self): self._selected_date = date.today(); self.refresh()
