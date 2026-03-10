"""
SelfMaster - Ideal Self Tab
Define and manage criteria of the ideal person + daily scoring.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from .theme import *
from .widgets import *
from db import queries as Q


CATEGORIES = [
    ("physical",  "💪 Фізичне"),
    ("mental",    "🧠 Ментальне"),
    ("social",    "❤️ Соціальне"),
    ("financial", "💰 Фінансове"),
    ("spiritual", "🧘 Духовне"),
    ("other",     "🎨 Інше"),
]

ICONS = ["🎯","💪","🧠","❤️","💰","🧘","📚","🎨","🏃","🌱","🤝","🔥","⭐","🎯","📈","🌟","🏆","✅"]


class IdealTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        # Top: add criterion button
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(16, 8))

        tk.Label(top, text="ІДЕАЛЬНА ЛЮДИНА", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(top, text="+ Додати критерій", command=self._show_add_dialog,
                  bg=ACCENT, fg=BG, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=12, pady=6).pack(side="right")

        # Intro card
        intro = tk.Frame(self, bg=SURFACE, padx=16, pady=12)
        intro.pack(fill="x", padx=20, pady=(0, 12))
        tk.Frame(intro, bg=ACCENT2, height=2).pack(fill="x")
        tk.Label(intro, text=(
            "Визнач критерії ідеальної людини та оцінюй себе щодня за шкалою 0–5.\n"
            "Це допоможе зрозуміти, де ти зараз і куди рухатись."
        ), bg=SURFACE, fg=TEXT_DIM, font=FONT_MAIN, justify="left", anchor="w").pack(
            fill="x", pady=(8, 0))

        # Category filter
        filter_frame = tk.Frame(self, bg=BG)
        filter_frame.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(filter_frame, text="Категорія:", bg=BG, fg=TEXT_DIM,
                 font=FONT_MONO).pack(side="left", padx=(0, 8))
        self._cat_var = tk.StringVar(value="all")
        for val, lbl in [("all", "Всі")] + CATEGORIES:
            tk.Radiobutton(filter_frame, text=lbl, variable=self._cat_var,
                           value=val, bg=BG, fg=TEXT_DIM,
                           selectcolor=BG, activebackground=BG,
                           font=FONT_MONO, command=self.refresh).pack(side="left", padx=4)

        # Main area with scroll
        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20)

        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        criteria = Q.get_ideal_criteria()
        cat_filter = self._cat_var.get()

        if cat_filter != "all":
            criteria = [c for c in criteria if c['category'] == cat_filter]

        if not criteria:
            tk.Label(self._scroll, text="Немає критеріїв. Натисніть '+ Додати критерій'.",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=30)
            return

        # Group by category
        from collections import defaultdict
        grouped = defaultdict(list)
        for c in criteria:
            grouped[c['category']].append(c)

        today = date.today()
        scores = {s['criterion_id']: s for s in Q.get_ideal_scores_for_date(today)}

        for cat, items in grouped.items():
            color = CATEGORY_COLORS.get(cat, ACCENT3)
            cat_label_dict = dict(CATEGORIES)
            cat_lbl = cat_label_dict.get(cat, cat.title())

            # Category header
            cat_frame = tk.Frame(self._scroll, bg=SURFACE)
            cat_frame.pack(fill="x", pady=(0, 2))
            tk.Frame(cat_frame, bg=color, height=2).pack(fill="x")
            tk.Label(cat_frame, text=cat_lbl, bg=SURFACE, fg=color,
                     font=("Segoe UI", 11, "bold"), padx=14, pady=8).pack(anchor="w")

            for i, crit in enumerate(items):
                cid = crit['id']
                score_data = scores.get(cid)
                score = score_data['score'] if score_data else None

                row = tk.Frame(self._scroll, bg=SURFACE if i % 2 == 0 else SURFACE2,
                               padx=14, pady=10)
                row.pack(fill="x")

                # Icon + info
                tk.Label(row, text=crit['icon'], bg=row['bg'],
                         font=("Segoe UI", 16)).pack(side="left", padx=(0, 10))

                info = tk.Frame(row, bg=row['bg'])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=crit['title'], bg=row['bg'],
                         fg=TEXT, font=FONT_BOLD, anchor="w").pack(anchor="w")
                if crit.get('description'):
                    tk.Label(info, text=crit['description'], bg=row['bg'],
                             fg=TEXT_DIM, font=FONT_MONO, anchor="w").pack(anchor="w")

                # Score for today
                score_lbl_text = "Не оцінено" if score is None else self._score_label(score)
                score_color = TEXT_DIM if score is None else color
                tk.Label(info, text=f"Сьогодні: {score_lbl_text}",
                         bg=row['bg'], fg=score_color, font=FONT_MONO).pack(anchor="w")

                # Avg last 7 days
                history = self._get_recent_scores(cid, 7)
                if history:
                    avg = sum(history) / len(history)
                    stars = "●" * int(round(avg)) + "○" * (5 - int(round(avg)))
                    tk.Label(info, text=f"Серед. 7 днів: {stars} ({avg:.1f})",
                             bg=row['bg'], fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

                # Buttons: edit, delete
                btn_frame = tk.Frame(row, bg=row['bg'])
                btn_frame.pack(side="right")

                tk.Button(btn_frame, text="✎",
                          command=lambda c=crit: self._show_edit_dialog(c),
                          bg=SURFACE2, fg=ACCENT3, font=("Segoe UI", 11),
                          relief="flat", cursor="hand2", width=3).pack(side="left", padx=2)

                tk.Button(btn_frame, text="✕",
                          command=lambda c=crit: self._delete(c),
                          bg=SURFACE2, fg=FAIL, font=("Segoe UI", 11),
                          relief="flat", cursor="hand2", width=3).pack(side="left")

        # Summary stats
        self._build_summary(criteria, scores)

    def _get_recent_scores(self, criterion_id, days=7):
        from datetime import timedelta
        from db.database import get_session
        from db.models import IdealScore
        from_date = date.today() - timedelta(days=days)
        with get_session() as s:
            rows = (
                s.query(IdealScore.score)
                .filter(
                    IdealScore.criterion_id == criterion_id,
                    IdealScore.score_date >= from_date,
                )
                .all()
            )
        return [r.score for r in rows]

    def _score_label(self, score):
        labels = {0: "0 — Нічого", 1: "1 — Слабко", 2: "2 — Нижче норми",
                  3: "3 — Нормально", 4: "4 — Добре", 5: "5 — Відмінно"}
        return labels.get(score, str(score))

    def _build_summary(self, criteria, scores):
        today = date.today()
        scored = len([c for c in criteria if c['id'] in scores])
        total = len(criteria)
        avg = sum(scores[s]['score'] for s in scores) / len(scores) if scores else 0

        summary = tk.Frame(self._scroll, bg=SURFACE, padx=14, pady=12)
        summary.pack(fill="x", pady=(12, 0))
        tk.Frame(summary, bg=STREAK, height=2).pack(fill="x")

        row = tk.Frame(summary, bg=SURFACE)
        row.pack(fill="x", pady=(8, 0))

        for label, val, color in [
            ("Оцінено сьогодні", f"{scored}/{total}", ACCENT),
            ("Середній бал", f"{avg:.1f}/5.0", ACCENT2),
            ("Дата", today.strftime("%d.%m.%Y"), ACCENT3),
        ]:
            f = tk.Frame(row, bg=SURFACE, padx=20)
            f.pack(side="left")
            tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 8)).pack()
            tk.Label(f, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI", 16, "bold")).pack()

    def _show_add_dialog(self):
        self._show_criterion_dialog(None)

    def _show_edit_dialog(self, crit):
        self._show_criterion_dialog(crit)

    def _show_criterion_dialog(self, crit):
        win = tk.Toplevel()
        title = "Редагувати критерій" if crit else "Новий критерій"
        win.title(title)
        win.configure(bg=SURFACE2)
        win.geometry("420x460")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=title, bg=SURFACE2, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(padx=20, pady=(16, 12), anchor="w")

        # Fields
        fields_frame = tk.Frame(win, bg=SURFACE2)
        fields_frame.pack(fill="x", padx=20)

        # Title
        _, title_var = labeled_entry(fields_frame, "Назва", bg=SURFACE2, width=40)
        if crit:
            title_var.set(crit['title'])
        title_lbl_f = fields_frame.winfo_children()[-1]
        title_lbl_f.pack(fill="x", pady=(0, 8))

        # Description
        tk.Label(fields_frame, text="Опис", bg=SURFACE2, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w")
        desc_txt = tk.Text(fields_frame, height=2, bg=SURFACE, fg=TEXT,
                           font=FONT_MAIN, relief="flat", insertbackground=TEXT,
                           wrap="word", highlightthickness=1,
                           highlightbackground=BORDER, highlightcolor=ACCENT3, bd=4)
        desc_txt.pack(fill="x", pady=(2, 8))
        if crit and crit.get('description'):
            desc_txt.insert("1.0", crit['description'])

        # Category
        tk.Label(fields_frame, text="Категорія", bg=SURFACE2, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w")
        cat_var = tk.StringVar(value=crit['category'] if crit else "physical")
        cat_menu = ttk.Combobox(fields_frame, textvariable=cat_var,
                                values=[v for v, _ in CATEGORIES],
                                state="readonly", width=20)
        cat_menu.pack(anchor="w", pady=(2, 8))

        # Icon picker
        tk.Label(fields_frame, text="Іконка", bg=SURFACE2, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w")
        icon_var = tk.StringVar(value=crit['icon'] if crit else "🎯")

        icon_frame = tk.Frame(fields_frame, bg=SURFACE2)
        icon_frame.pack(fill="x", pady=(2, 12))

        icon_lbl = tk.Label(icon_frame, textvariable=icon_var,
                            bg=SURFACE, fg=TEXT, font=("Segoe UI", 18), width=3)
        icon_lbl.pack(side="left", padx=(0, 8))

        icons_grid = tk.Frame(icon_frame, bg=SURFACE2)
        icons_grid.pack(side="left")
        for j, ic in enumerate(ICONS):
            btn = tk.Label(icons_grid, text=ic, bg=SURFACE2,
                           font=("Segoe UI", 12), cursor="hand2")
            btn.grid(row=j//9, column=j%9, padx=1, pady=1)
            btn.bind("<Button-1>", lambda e, ic=ic: icon_var.set(ic))

        # Save button
        def save():
            t = title_var.get().strip()
            if not t:
                return
            d = desc_txt.get("1.0", "end-1c").strip()
            if crit:
                Q.update_ideal_criterion(crit['id'],
                                         title=t, description=d,
                                         category=cat_var.get(),
                                         icon=icon_var.get())
            else:
                Q.add_ideal_criterion(cat_var.get(), t, icon_var.get(), d)
            win.destroy()
            self.refresh()

        tk.Button(win, text="💾 Зберегти", command=save,
                  bg=ACCENT, fg=BG, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=16, pady=8).pack(padx=20, pady=12)

    def _delete(self, crit):
        if messagebox.askyesno("Видалити?", f"Видалити '{crit['title']}'?\nВсі оцінки також будуть видалені."):
            Q.delete_ideal_criterion(crit['id'])
            self.refresh()
