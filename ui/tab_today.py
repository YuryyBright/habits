"""
SelfMaster - Today Tab
Daily habit check-in + journal + ideal self scoring.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, timedelta
from .theme import *
from .widgets import *
from db import queries as Q


class TodayTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._selected_date = date.today()
        self._habit_widgets = {}
        self._ideal_widgets = {}
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────
    def _build(self):
        # Top bar: date nav
        nav = tk.Frame(self, bg=BG)
        nav.pack(fill="x", padx=20, pady=(16, 8))

        tk.Button(nav, text="‹", bg=SURFACE2, fg=TEXT,
                  font=("Segoe UI", 14), relief="flat", cursor="hand2",
                  command=self._prev_day).pack(side="left")

        self._date_var = tk.StringVar()
        tk.Label(nav, textvariable=self._date_var, bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=16)

        tk.Button(nav, text="›", bg=SURFACE2, fg=TEXT,
                  font=("Segoe UI", 14), relief="flat", cursor="hand2",
                  command=self._next_day).pack(side="left")

        today_btn = tk.Button(nav, text="Сьогодні", bg=SURFACE2, fg=ACCENT3,
                              font=FONT_MONO, relief="flat", cursor="hand2",
                              command=self._go_today)
        today_btn.pack(side="left", padx=(16, 0))

        # Mood/energy row
        self._mood_frame = tk.Frame(self, bg=BG)
        self._mood_frame.pack(fill="x", padx=20, pady=(0, 8))
        self._build_mood_row()

        # Main scroll area
        scroll_outer, self._scroll_inner = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=8)

        self.refresh()

    def _build_mood_row(self):
        for w in self._mood_frame.winfo_children():
            w.destroy()

        f = tk.Frame(self._mood_frame, bg=SURFACE, padx=14, pady=10)
        f.pack(fill="x")
        tk.Frame(f, bg=ACCENT2, height=2).pack(fill="x")

        inner = tk.Frame(f, bg=SURFACE)
        inner.pack(fill="x", pady=(6, 0))

        tk.Label(inner, text="Настрій:", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_MONO).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self._mood_picker = MoodPicker(inner, initial=3, callback=self._save_journal_meta)
        self._mood_picker.grid(row=0, column=1, sticky="w")

        tk.Label(inner, text="Енергія:", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_MONO).grid(row=0, column=2, sticky="w", padx=(20, 8))
        self._energy_picker = MoodPicker(inner, initial=3, callback=self._save_journal_meta)
        self._energy_picker.grid(row=0, column=3, sticky="w")

    # ── Refresh ───────────────────────────────────────────────────────────
    def refresh(self):
        d = self._selected_date
        is_today = (d == date.today())

        # Date label
        days = ["Понеділок","Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]
        months = ["Січня","Лютого","Березня","Квітня","Травня","Червня",
                  "Липня","Серпня","Вересня","Жовтня","Листопада","Грудня"]
        label = f"{days[d.weekday()]}, {d.day} {months[d.month-1]} {d.year}"
        if is_today:
            label += "  •  Сьогодні"
        self._date_var.set(label)

        # Load journal
        journal = Q.get_journal(d)
        if journal:
            self._mood_picker.set(journal.get('mood', 3))
            self._energy_picker.set(journal.get('energy', 3))

        self._clear_scroll()
        self._build_habits_section()
        self._build_ideal_section()
        self._build_journal_section()

    def _clear_scroll(self):
        for w in self._scroll_inner.winfo_children():
            w.destroy()
        self._habit_widgets.clear()
        self._ideal_widgets.clear()

    # ── Habits Section ────────────────────────────────────────────────────
    def _build_habits_section(self):
        parent = self._scroll_inner
        d = self._selected_date
        habits = Q.get_habits()
        logs = Q.get_logs_for_month(d.year, d.month)
        is_future = d > date.today()

        # Header
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="ЗВИЧКИ", bg=BG, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(side="left")
        sep = tk.Frame(hdr, bg=BORDER, height=1)
        sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

        card = tk.Frame(parent, bg=SURFACE, padx=0, pady=0)
        card.pack(fill="x", pady=(0, 12))
        tk.Frame(card, bg=ACCENT, height=2).pack(fill="x")

        if not habits:
            tk.Label(card, text="Немає звичок. Додайте їх у вкладці 'Звички'.",
                     bg=SURFACE, fg=TEXT_DIM, font=FONT_MAIN).pack(padx=16, pady=20)
            return

        for i, h in enumerate(habits):
            hid = h['id']
            day_logs = logs.get(hid, {})
            val = day_logs.get(d.day)

            row = tk.Frame(card, bg=SURFACE if i % 2 == 0 else SURFACE2)
            row.pack(fill="x")
            row.bind("<Enter>", lambda e, r=row: r.configure(bg=BORDER))
            row.bind("<Leave>", lambda e, r=row, i=i: r.configure(
                bg=SURFACE if i % 2 == 0 else SURFACE2))

            # Emoji + Name
            tk.Label(row, text=h['emoji'], bg=row['bg'],
                     font=("Segoe UI", 14)).pack(side="left", padx=(14, 6), pady=8)
            tk.Label(row, text=h['name'], bg=row['bg'],
                     fg=TEXT, font=FONT_BOLD).pack(side="left")

            if h.get('unit'):
                tk.Label(row, text=f"({h['unit']})", bg=row['bg'],
                         fg=TEXT_DIM, font=FONT_MONO).pack(side="left", padx=4)

            # Streak badge
            cur_s, _ = Q.get_habit_streak(hid)
            if cur_s >= 2:
                tk.Label(row, text=f"🔥 {cur_s}", bg=row['bg'],
                         fg=STREAK, font=FONT_MONO).pack(side="left", padx=8)

            # Right side: action buttons
            btn_frame = tk.Frame(row, bg=row['bg'])
            btn_frame.pack(side="right", padx=12, pady=6)

            self._build_habit_controls(btn_frame, h, val, d, is_future, row)

    def _build_habit_controls(self, parent, habit, current_val, log_date, is_future, row_frame):
        hid = habit['id']
        htype = habit['type']

        if is_future:
            tk.Label(parent, text="буд.", bg=parent['bg'],
                     fg=TEXT_DIM, font=FONT_MONO).pack(side="right")
            return

        def done_val():
            return 'done' if htype == 'toggle' else None

        def _set(val):
            if val is None:
                Q.clear_log(hid, log_date)
            else:
                Q.log_habit(hid, log_date, val)
            self.refresh()

        # Done / Fail for toggle
        if htype == 'toggle':
            is_done = current_val == 'done'
            is_fail = current_val == 'fail'

            done_btn = tk.Label(parent, text="✔", cursor="hand2",
                                bg=DONE + "22" if is_done else SURFACE2,
                                fg=DONE if is_done else TEXT_DIM,
                                font=("Segoe UI", 12), width=3, relief="flat")
            done_btn.pack(side="right", padx=2)
            done_btn.bind("<Button-1>", lambda e: _set(None if is_done else 'done'))

            fail_btn = tk.Label(parent, text="✖", cursor="hand2",
                                bg=FAIL + "22" if is_fail else SURFACE2,
                                fg=FAIL if is_fail else TEXT_DIM,
                                font=("Segoe UI", 12), width=3, relief="flat")
            fail_btn.pack(side="right", padx=2)
            fail_btn.bind("<Button-1>", lambda e: _set(None if is_fail else 'fail'))

        elif htype == 'number':
            # Display current value
            val_display = current_val if current_val is not None else "—"

            # Color based on goal
            val_color = TEXT_DIM
            if current_val is not None:
                try:
                    n = float(current_val)
                    if habit.get('is_negative'):
                        val_color = DONE if n == 0 else (STREAK if n <= 5 else FAIL)
                    else:
                        goal = habit.get('goal_value') or 1
                        val_color = DONE if n >= goal else (ACCENT3 if n > 0 else TEXT_DIM)
                except:
                    pass

            lbl = tk.Label(parent, text=str(val_display),
                           bg=parent['bg'], fg=val_color,
                           font=("Consolas", 13, "bold"), width=5)
            lbl.pack(side="right", padx=4)

            # +/- buttons
            def _increment(delta):
                try:
                    cur = float(current_val) if current_val is not None else 0
                    new_val = max(0, cur + delta)
                    Q.log_habit(hid, log_date, int(new_val) if new_val == int(new_val) else new_val)
                    self.refresh()
                except:
                    pass

            plus = tk.Label(parent, text="+", cursor="hand2",
                            bg=SURFACE2, fg=ACCENT3, font=("Segoe UI", 13, "bold"),
                            width=2)
            plus.pack(side="right", padx=1)
            plus.bind("<Button-1>", lambda e: _increment(1))

            minus = tk.Label(parent, text="−", cursor="hand2",
                             bg=SURFACE2, fg=TEXT_DIM, font=("Segoe UI", 13, "bold"),
                             width=2)
            minus.pack(side="right", padx=1)
            minus.bind("<Button-1>", lambda e: _increment(-1))

            # Manual input
            def _edit():
                win = tk.Toplevel()
                win.title(f"{habit['emoji']} {habit['name']}")
                win.configure(bg=SURFACE2)
                win.geometry("240x120")
                win.resizable(False, False)
                tk.Label(win, text=f"Введіть значення ({habit.get('unit','')}):",
                         bg=SURFACE2, fg=TEXT, font=FONT_MAIN).pack(pady=(16, 4))
                var = tk.StringVar(value=str(current_val) if current_val else "")
                e = tk.Entry(win, textvariable=var, bg=SURFACE, fg=TEXT,
                             insertbackground=TEXT,
                             justify="center", font=("Consolas", 14))
                e.pack(padx=20, fill="x")
                e.focus_set()
                e.select_range(0, "end")
                def confirm(ev=None):
                    try:
                        n = float(var.get())
                        Q.log_habit(hid, log_date, int(n) if n == int(n) else n)
                        win.destroy()
                        self.refresh()
                    except:
                        pass
                def clear_val(ev=None):
                    Q.clear_log(hid, log_date)
                    win.destroy()
                    self.refresh()
                e.bind("<Return>", confirm)
                tk.Button(win, text="ОК", command=confirm, bg=ACCENT, fg=BG,
                          font=FONT_BOLD, relief="flat").pack(side="left", padx=(20, 4), pady=8)
                tk.Button(win, text="Очистити", command=clear_val, bg=SURFACE, fg=FAIL,
                          font=FONT_MONO, relief="flat").pack(side="left")

            edit_btn = tk.Label(parent, text="✎", cursor="hand2",
                                bg=SURFACE2, fg=TEXT_DIM, font=("Segoe UI", 11), width=2)
            edit_btn.pack(side="right", padx=1)
            edit_btn.bind("<Button-1>", lambda e: _edit())

            # Quick zero for negative habits
            if habit.get('is_negative'):
                zero_btn = tk.Label(parent, text="0", cursor="hand2",
                                    bg=DONE + "22" if current_val == '0' or current_val == 0 else SURFACE2,
                                    fg=DONE, font=FONT_MONO, width=2)
                zero_btn.pack(side="right", padx=1)
                zero_btn.bind("<Button-1>", lambda e: (_set(0), None)[1])

    # ── Ideal Self Section ────────────────────────────────────────────────
    def _build_ideal_section(self):
        parent = self._scroll_inner
        d = self._selected_date

        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", pady=(8, 6))
        tk.Label(hdr, text="ІДЕАЛЬНА ЛЮДИНА", bg=BG, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(side="left")
        sep = tk.Frame(hdr, bg=BORDER, height=1)
        sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

        criteria = Q.get_ideal_criteria()
        scores_today = {s['criterion_id']: s for s in Q.get_ideal_scores_for_date(d)}

        if not criteria:
            card = tk.Frame(parent, bg=SURFACE, padx=16, pady=12)
            card.pack(fill="x", pady=(0, 12))
            tk.Frame(card, bg=ACCENT2, height=2).pack(fill="x")
            tk.Label(card, text="Немає критеріїв. Додайте їх у вкладці 'Ідеальна Людина'.",
                     bg=SURFACE, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=12)
            return

        # Group by category
        from collections import defaultdict
        grouped = defaultdict(list)
        for c in criteria:
            grouped[c['category']].append(c)

        cat_colors = {
            "physical": ACCENT, "mental": ACCENT3, "social": ACCENT2,
            "financial": STREAK, "spiritual": "#a78bfa",
            "health": ACCENT, "mind": ACCENT3, "other": TEXT_DIM, "general": TEXT_DIM
        }

        for cat, items in grouped.items():
            cat_color = cat_colors.get(cat, ACCENT3)
            cat_label = CATEGORY_LABELS.get(cat, cat.title())

            card = tk.Frame(parent, bg=SURFACE)
            card.pack(fill="x", pady=(0, 8))
            tk.Frame(card, bg=cat_color, height=2).pack(fill="x")

            cat_hdr = tk.Frame(card, bg=SURFACE, padx=14, pady=8)
            cat_hdr.pack(fill="x")
            tk.Label(cat_hdr, text=f"{cat_label}",
                     bg=SURFACE, fg=cat_color, font=FONT_BOLD).pack(side="left")

            for i, crit in enumerate(items):
                cid = crit['id']
                score_data = scores_today.get(cid)
                score = score_data['score'] if score_data else 0

                row = tk.Frame(card, bg=SURFACE if i % 2 == 0 else SURFACE2,
                               padx=14, pady=6)
                row.pack(fill="x")

                tk.Label(row, text=crit['icon'], bg=row['bg'],
                         font=("Segoe UI", 12)).pack(side="left", padx=(0, 8))

                info = tk.Frame(row, bg=row['bg'])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=crit['title'], bg=row['bg'],
                         fg=TEXT, font=FONT_BOLD, anchor="w").pack(anchor="w")
                if crit.get('description'):
                    tk.Label(info, text=crit['description'], bg=row['bg'],
                             fg=TEXT_DIM, font=FONT_MONO, anchor="w").pack(anchor="w")

                # Score slider (right side)
                score_frame = tk.Frame(row, bg=row['bg'])
                score_frame.pack(side="right")

                slider = ScoreSlider(score_frame, initial=score,
                                     callback=lambda v, c=cid: self._save_ideal_score(c, v))
                slider.configure(bg=row['bg'])
                # Update slider bg for all children
                for child in slider.winfo_children():
                    child.configure(bg=row['bg'])
                slider.pack()

                # Score label
                score_labels = {0: "—", 1: "Слабко", 2: "Нижче норми",
                                3: "Нормально", 4: "Добре", 5: "Відмінно"}
                score_lbl = tk.Label(score_frame, text=score_labels.get(score, ""),
                                     bg=row['bg'], fg=cat_color if score > 0 else TEXT_DIM,
                                     font=("Consolas", 8), width=12)
                score_lbl.pack()
                self._ideal_widgets[cid] = score_lbl

    def _save_ideal_score(self, criterion_id, score):
        Q.score_ideal(criterion_id, self._selected_date, score)
        # Update label
        if criterion_id in self._ideal_widgets:
            labels = {0: "—", 1: "Слабко", 2: "Нижче норми",
                      3: "Нормально", 4: "Добре", 5: "Відмінно"}
            self._ideal_widgets[criterion_id].configure(text=labels.get(score, ""))

    # ── Journal Section ───────────────────────────────────────────────────
    def _build_journal_section(self):
        parent = self._scroll_inner
        d = self._selected_date
        journal = Q.get_journal(d)

        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", pady=(8, 6))
        tk.Label(hdr, text="ЩОДЕННИК", bg=BG, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(side="left")
        sep = tk.Frame(hdr, bg=BORDER, height=1)
        sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=10)

        card = tk.Frame(parent, bg=SURFACE, padx=14, pady=12)
        card.pack(fill="x", pady=(0, 12))
        tk.Frame(card, bg=ACCENT3, height=2).pack(fill="x")

        fields = [
            ("📝 Нотатки дня", "content", "Що відбувалось сьогодні?", 4),
            ("🏆 Перемоги дня", "wins", "Чим пишаєшся сьогодні?", 2),
            ("🎯 Плани на завтра", "tomorrow", "Що зробиш завтра?", 2),
        ]

        self._journal_vars = {}
        for label, key, placeholder, height in fields:
            tk.Label(card, text=label, bg=SURFACE, fg=TEXT_DIM,
                     font=FONT_MONO, anchor="w").pack(fill="x", pady=(8, 2))
            txt = tk.Text(card, height=height, bg=SURFACE2, fg=TEXT,
                          font=("Segoe UI", 10), relief="flat",
                          insertbackground=TEXT, wrap="word",
                          highlightthickness=1, highlightbackground=BORDER,
                          highlightcolor=ACCENT3, bd=4)
            txt.pack(fill="x")
            if journal and journal.get(key):
                txt.insert("1.0", journal[key])
            else:
                txt.insert("1.0", "")
            self._journal_vars[key] = txt

        # Save button
        def save_journal():
            Q.save_journal(
                d,
                mood=self._mood_picker.get(),
                energy=self._energy_picker.get(),
                content=self._journal_vars['content'].get("1.0", "end-1c"),
                wins=self._journal_vars['wins'].get("1.0", "end-1c"),
                tomorrow=self._journal_vars['tomorrow'].get("1.0", "end-1c"),
            )
            # Flash feedback
            save_btn.configure(text="✔ Збережено!", fg=DONE)
            card.after(2000, lambda: save_btn.configure(text="💾 Зберегти", fg=TEXT))

        save_btn = tk.Button(card, text="💾 Зберегти", command=save_journal,
                             bg=SURFACE2, fg=TEXT, font=FONT_BOLD,
                             relief="flat", cursor="hand2", pady=6)
        save_btn.pack(anchor="e", pady=(10, 0))

    def _save_journal_meta(self, _=None):
        d = self._selected_date
        j = Q.get_journal(d)
        Q.save_journal(
            d,
            mood=self._mood_picker.get(),
            energy=self._energy_picker.get(),
            content=j['content'] if j else "",
            wins=j['wins'] if j else "",
            tomorrow=j['tomorrow'] if j else "",
        )

    # ── Navigation ────────────────────────────────────────────────────────
    def _prev_day(self):
        self._selected_date -= timedelta(days=1)
        self.refresh()

    def _next_day(self):
        if self._selected_date < date.today():
            self._selected_date += timedelta(days=1)
            self.refresh()

    def _go_today(self):
        self._selected_date = date.today()
        self.refresh()
