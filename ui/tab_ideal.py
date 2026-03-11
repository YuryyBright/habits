"""SelfMaster — Ideal Self Tab"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from collections import defaultdict
from ui import *
import db

CATEGORIES = [("physical","💪 Фізичне"),("mental","🧠 Ментальне"),("social","❤️ Соціальне"),
              ("financial","💰 Фінансове"),("spiritual","🧘 Духовне"),("other","🎨 Інше")]
ICONS = ["🎯","💪","🧠","❤️","💰","🧘","📚","🎨","🏃","🌱","🤝","🔥","⭐","📈","🌟","🏆","✅","😊"]


class IdealTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._cat_var = tk.StringVar(value="all")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr, text="ІДЕАЛЬНА ЛЮДИНА", bg=SURFACE, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")
        add_btn = tk.Label(hdr, text="＋  Додати критерій",
                           bg=_hex_fade(ACCENT2,0.2), fg=ACCENT2,
                           font=FONT_BOLD, cursor="hand2", padx=14, pady=8)
        add_btn.pack(side="right")
        add_btn.bind("<Button-1>", lambda e: self._show_dialog(None))
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=_hex_fade(ACCENT2,0.35)))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=_hex_fade(ACCENT2,0.2)))

        # Intro
        intro = tk.Frame(self, bg=SURFACE2, padx=20, pady=10)
        intro.pack(fill="x", padx=20, pady=(12,0))
        tk.Label(intro, text=(
            "Визнач критерії ідеальної людини та оцінюй себе щодня за шкалою 0–5.\n"
            "Це допоможе зрозуміти, де ти зараз і куди рухатись."
        ), bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO, justify="left").pack(anchor="w")

        # Category filter
        filter_f = tk.Frame(self, bg=BG, padx=20, pady=8)
        filter_f.pack(fill="x")
        tk.Label(filter_f, text="Фільтр:", bg=BG, fg=TEXT_DIM,
                 font=FONT_MONO).pack(side="left", padx=(0,8))

        self._filter_btns = {}
        for val, lbl in [("all","Всі")] + CATEGORIES:
            b = tk.Label(filter_f, text=lbl, bg=SURFACE2, fg=TEXT_DIM,
                         font=FONT_MONO, cursor="hand2", padx=8, pady=4)
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, v=val: self._set_filter(v))
            self._filter_btns[val] = b
        self._set_filter("all", init=True)

        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=4)
        self.refresh()

    def _set_filter(self, val, init=False):
        self._cat_var.set(val)
        for k, b in self._filter_btns.items():
            if k == val:
                color = ACCENT2 if k != "all" else ACCENT
                b.configure(bg=_hex_fade(color,0.25), fg=color)
            else:
                b.configure(bg=SURFACE2, fg=TEXT_DIM)
        if not init: self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        criteria = db.get_ideal_criteria()
        cat_filter = self._cat_var.get()
        if cat_filter != "all":
            criteria = [c for c in criteria if c['category'] == cat_filter]

        if not criteria:
            tk.Label(self._scroll, text="Немає критеріїв. Натисніть '+ Додати критерій'.",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=40)
            return

        grouped = defaultdict(list)
        for c in criteria:
            grouped[c['category']].append(c)

        today = date.today()
        scores = {s['criterion_id']: s for s in db.get_ideal_scores_for_date(today)}

        for cat, items in grouped.items():
            color = CATEGORY_COLORS.get(cat, ACCENT3)
            cat_lbl = CATEGORY_LABELS.get(cat, cat)

            cat_f = tk.Frame(self._scroll, bg=SURFACE)
            cat_f.pack(fill="x", pady=(0,4))
            tk.Frame(cat_f, bg=color, height=2).pack(fill="x")
            tk.Label(cat_f, text=cat_lbl, bg=SURFACE, fg=color,
                     font=("Segoe UI",11,"bold"), padx=16, pady=8).pack(anchor="w")

            for i, crit in enumerate(items):
                cid = crit['id']
                score_data = scores.get(cid)
                score = score_data['score'] if score_data else None

                row_bg = SURFACE if i%2==0 else SURFACE2
                row = tk.Frame(self._scroll, bg=row_bg, padx=16, pady=10)
                row.pack(fill="x")

                tk.Label(row, text=crit['icon'], bg=row_bg,
                         font=("Segoe UI",15)).pack(side="left", padx=(0,10))

                info = tk.Frame(row, bg=row_bg)
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=crit['title'], bg=row_bg, fg=TEXT,
                         font=FONT_BOLD).pack(anchor="w")
                if crit.get('description'):
                    tk.Label(info, text=crit['description'], bg=row_bg,
                             fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

                # Score display
                score_lbl = "Не оцінено" if score is None else self._score_lbl(score)
                score_clr = TEXT_DIM if score is None else color
                tk.Label(info, text=f"Сьогодні: {score_lbl}",
                         bg=row_bg, fg=score_clr, font=FONT_MONO).pack(anchor="w")

                # Recent avg
                history = self._recent_scores(cid, 7)
                if history:
                    avg = sum(history)/len(history)
                    stars = "●"*int(round(avg)) + "○"*(5-int(round(avg)))
                    tk.Label(info, text=f"Сер. 7 днів: {stars} ({avg:.1f})",
                             bg=row_bg, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

                # Buttons
                btn_f = tk.Frame(row, bg=row_bg)
                btn_f.pack(side="right")
                self._btn(btn_f, "✎", lambda c=crit: self._show_dialog(c), ACCENT3)
                self._btn(btn_f, "✕", lambda c=crit: self._delete(c), FAIL)

        self._build_summary(criteria, scores)

    def _btn(self, parent, text, cmd, color):
        b = tk.Label(parent, text=text, bg=SURFACE3, fg=color,
                     font=FONT_MONO, cursor="hand2", padx=8, pady=4)
        b.pack(side="left", padx=2)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=_hex_fade(color,0.2)))
        b.bind("<Leave>", lambda e: b.configure(bg=SURFACE3))

    def _recent_scores(self, criterion_id, days=7):
        from datetime import timedelta
        from_date = date.today() - timedelta(days=days)
        with db.get_conn() as conn:
            rows = conn.execute(
                "SELECT score FROM ideal_scores WHERE criterion_id=? AND score_date>=?",
                (criterion_id, from_date.isoformat())
            ).fetchall()
        return [r['score'] for r in rows]

    def _score_lbl(self, score):
        labels = {0:"0 — Нічого",1:"1 — Слабко",2:"2 — Нижче норми",
                  3:"3 — Нормально",4:"4 — Добре",5:"5 — Відмінно"}
        return labels.get(score, str(score))

    def _build_summary(self, criteria, scores):
        today = date.today()
        scored = len([c for c in criteria if c['id'] in scores])
        total = len(criteria)
        avg = sum(scores[s]['score'] for s in scores)/len(scores) if scores else 0

        s = tk.Frame(self._scroll, bg=SURFACE, padx=16, pady=12)
        s.pack(fill="x", pady=(12,0))
        tk.Frame(s, bg=STREAK, height=2).pack(fill="x")

        row = tk.Frame(s, bg=SURFACE)
        row.pack(fill="x", pady=(10,0))

        for label, val, color in [
            ("Оцінено сьогодні", f"{scored}/{total}", ACCENT),
            ("Середній бал", f"{avg:.1f}/5.0", ACCENT2),
            ("Дата", today.strftime("%d.%m.%Y"), ACCENT3),
        ]:
            f = tk.Frame(row, bg=SURFACE, padx=20)
            f.pack(side="left")
            tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",8)).pack()
            tk.Label(f, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI",16,"bold")).pack()

    def _show_dialog(self, crit):
        win = tk.Toplevel(self)
        title = "Редагувати критерій" if crit else "Новий критерій"
        win.title(title)
        win.configure(bg=SURFACE)
        win.geometry("420x440")
        win.resizable(False, False)
        win.grab_set()

        hdr = tk.Frame(win, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr, text=title, bg=SURFACE, fg=TEXT, font=FONT_TITLE).pack(anchor="w")

        f = tk.Frame(win, bg=SURFACE, padx=24)
        f.pack(fill="x", pady=12)

        _, title_var = labeled_entry(f, "Назва *", bg=SURFACE, width=38)
        if crit: title_var.set(crit['title'])
        f.winfo_children()[-1].pack(fill="x", pady=(0,10))

        tk.Label(f, text="Опис", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        desc_txt = tk.Text(f, height=2, bg=SURFACE2, fg=TEXT, font=FONT_MAIN,
                           relief="flat", insertbackground=TEXT, wrap="word",
                           highlightthickness=1, highlightbackground=BORDER,
                           highlightcolor=ACCENT, bd=6)
        desc_txt.pack(fill="x", pady=(3,10))
        if crit and crit.get('description'): desc_txt.insert("1.0", crit['description'])

        tk.Label(f, text="Категорія", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        cat_var = tk.StringVar(value=crit['category'] if crit else "physical")
        cat_menu = ttk.Combobox(f, textvariable=cat_var,
                                values=[v for v,_ in CATEGORIES],
                                state="readonly", width=22)
        cat_menu.pack(anchor="w", pady=(3,10))

        tk.Label(f, text="Іконка", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        icon_var = tk.StringVar(value=crit['icon'] if crit else "🎯")
        icon_f = tk.Frame(f, bg=SURFACE)
        icon_f.pack(fill="x", pady=(3,12))
        icon_lbl = tk.Label(icon_f, textvariable=icon_var, bg=SURFACE2,
                            font=("Segoe UI",18), width=3, pady=4)
        icon_lbl.pack(side="left", padx=(0,10))
        icons_grid = tk.Frame(icon_f, bg=SURFACE)
        icons_grid.pack(side="left")
        for j, ic in enumerate(ICONS):
            b = tk.Label(icons_grid, text=ic, bg=SURFACE, font=("Segoe UI",12), cursor="hand2")
            b.grid(row=j//9, column=j%9, padx=1, pady=1)
            b.bind("<Button-1>", lambda e, ic=ic: icon_var.set(ic))

        def save():
            t = title_var.get().strip()
            if not t: return
            d = desc_txt.get("1.0","end-1c").strip()
            if crit:
                db.update_ideal_criterion(crit['id'], title=t, description=d,
                                          category=cat_var.get(), icon=icon_var.get())
            else:
                db.add_ideal_criterion(cat_var.get(), t, icon_var.get(), d)
            win.destroy()
            self.refresh()

        save_btn = tk.Label(win, text="💾  Зберегти", bg=_hex_fade(ACCENT,0.2),
                            fg=ACCENT_L, font=FONT_BOLD, cursor="hand2", padx=20, pady=12)
        save_btn.pack(fill="x", padx=24, pady=(0,16))
        save_btn.bind("<Button-1>", lambda e: save())
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.35)))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.2)))

    def _delete(self, crit):
        if messagebox.askyesno("Видалити?",
                               f"Видалити '{crit['title']}'?\nВсі оцінки також будуть видалені."):
            db.delete_ideal_criterion(crit['id'])
            self.refresh()
