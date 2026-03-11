"""SelfMaster — Goals Tab"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from ui import *
import db
from ui.theme import *
GOAL_CATEGORIES = [
    ("health","❤️ Здоров'я"),("career","💼 Кар'єра"),
    ("financial","💰 Фінанси"),("personal","🌱 Розвиток"),
    ("social","🤝 Соціальне"),("other","📌 Інше"),
]
CATEGORY_COLORS_G = {
    "health":ACCENT,"career":ACCENT3,"financial":STREAK,
    "personal":ACCENT2,"social":ACCENT4,"other":TEXT_DIM
}


class GoalsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._status_var = tk.StringVar(value="active")
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr, text="МОЇ ЦІЛІ", bg=SURFACE, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")
        add_btn = tk.Label(hdr, text="＋  Нова ціль",
                           bg=_hex_fade(STREAK,0.2), fg=STREAK,
                           font=FONT_BOLD, cursor="hand2", padx=14, pady=8)
        add_btn.pack(side="right")
        add_btn.bind("<Button-1>", lambda e: self._show_dialog(None))
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=_hex_fade(STREAK,0.35)))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=_hex_fade(STREAK,0.2)))

        # Filter tabs
        filter_f = tk.Frame(self, bg=BG, padx=20, pady=10)
        filter_f.pack(fill="x")
        self._filter_btns = {}
        for val, lbl, clr in [("active","● Активні",ACCENT),
                               ("done","✔ Виконані",DONE),
                               ("paused","⏸ Пауза",STREAK)]:
            b = tk.Label(filter_f, text=lbl, bg=SURFACE2, fg=TEXT_DIM,
                         font=FONT_MONO, cursor="hand2", padx=12, pady=6)
            b.pack(side="left", padx=(0,6))
            b.bind("<Button-1>", lambda e, v=val: self._set_filter(v))
            self._filter_btns[val] = (b, clr)
        self._set_filter("active", init=True)

        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=4)
        self.refresh()

    def _set_filter(self, val, init=False):
        self._status_var.set(val)
        for k, (b, clr) in self._filter_btns.items():
            if k == val:
                b.configure(bg=_hex_fade(clr,0.25), fg=clr)
            else:
                b.configure(bg=SURFACE2, fg=TEXT_DIM)
        if not init: self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        goals = db.get_goals(self._status_var.get())
        if not goals:
            tk.Label(self._scroll, text="Немає цілей. Натисніть '+ Нова ціль'!",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=40)
            return

        for i, g in enumerate(goals):
            self._build_goal_card(g, i)

    def _build_goal_card(self, g, i):
        row_bg = SURFACE if i%2==0 else SURFACE2
        cat_color = CATEGORY_COLORS_G.get(g['category'], ACCENT3)

        card = tk.Frame(self._scroll, bg=row_bg, padx=0, pady=0)
        card.pack(fill="x", pady=(0,4))
        tk.Frame(card, bg=cat_color, height=2).pack(fill="x")

        inner = tk.Frame(card, bg=row_bg, padx=18, pady=12)
        inner.pack(fill="x")

        # Header
        hdr = tk.Frame(inner, bg=row_bg)
        hdr.pack(fill="x", pady=(0,6))

        tk.Label(hdr, text=g['title'], bg=row_bg, fg=TEXT,
                 font=("Segoe UI",12,"bold")).pack(side="left", fill="x", expand=True)

        status_cfg = {
            "active": ("● Активна", ACCENT),
            "done":   ("✔ Виконано", DONE),
            "paused": ("⏸ Пауза", STREAK),
        }
        slbl, sclr = status_cfg.get(g['status'], (g['status'], TEXT_DIM))
        tk.Label(hdr, text=slbl, bg=row_bg, fg=sclr, font=FONT_MONO).pack(side="right")

        # Description
        if g.get('description'):
            tk.Label(inner, text=g['description'], bg=row_bg, fg=TEXT_DIM,
                     font=FONT_MAIN, anchor="w", wraplength=580, justify="left").pack(
                anchor="w", pady=(0,8))

        # Meta
        meta = tk.Frame(inner, bg=row_bg)
        meta.pack(fill="x", pady=(0,10))
        cat_lbl = dict(GOAL_CATEGORIES).get(g['category'], g['category'])
        tk.Label(meta, text=cat_lbl, bg=row_bg, fg=cat_color,
                 font=FONT_MONO).pack(side="left", padx=(0,16))
        if g.get('deadline'):
            try:
                dl_date = date.fromisoformat(g['deadline'])
                days_left = (dl_date - date.today()).days
                dl_clr = FAIL if days_left < 7 else STREAK if days_left < 30 else TEXT_DIM
                tk.Label(meta, text=f"📅 {g['deadline']} ({days_left} д.)",
                         bg=row_bg, fg=dl_clr, font=FONT_MONO).pack(side="left", padx=(0,16))
            except:
                tk.Label(meta, text=f"📅 {g['deadline']}", bg=row_bg,
                         fg=TEXT_DIM, font=FONT_MONO).pack(side="left", padx=(0,16))
        if g.get('created_at'):
            tk.Label(meta, text=f"Створено: {g['created_at']}",
                     bg=row_bg, fg=TEXT_DIM, font=FONT_MONO).pack(side="right")

        # Progress bar
        prog = g.get('progress', 0)
        prog_clr = DONE if prog>=100 else cat_color

        prog_row = tk.Frame(inner, bg=row_bg)
        prog_row.pack(fill="x", pady=(0,6))
        tk.Label(prog_row, text=f"{prog}%", bg=row_bg, fg=prog_clr,
                 font=FONT_BOLD).pack(side="left", padx=(0,10))

        bar_outer = tk.Frame(prog_row, bg=SURFACE3, height=8)
        bar_outer.pack(side="left", fill="x", expand=True)
        bar_outer.pack_propagate(False)
        if prog > 0:
            tk.Frame(bar_outer, bg=prog_clr, height=8).place(relwidth=prog/100, relheight=1)

        # Slider
        prog_var = tk.IntVar(value=prog)
        bar_ref = [None]  # mutable ref for update

        def update_prog(val, gid=g['id']):
            v = int(float(val))
            db.update_goal(gid, progress=v)
            for w in bar_outer.winfo_children():
                w.destroy()
            clr = DONE if v>=100 else cat_color
            if v > 0:
                tk.Frame(bar_outer, bg=clr, height=8).place(relwidth=v/100, relheight=1)

        scale = ttk.Scale(inner, from_=0, to=100, orient="horizontal",
                          variable=prog_var, command=update_prog)
        scale.pack(fill="x", pady=(0,8))

        # Buttons
        btn_f = tk.Frame(inner, bg=row_bg)
        btn_f.pack(fill="x")

        self._btn(btn_f, "✎ Редагувати", lambda g=g: self._show_dialog(g), ACCENT3, row_bg)

        if g['status'] != 'done':
            self._btn(btn_f, "✔ Виконано",
                      lambda g=g: (db.update_goal(g['id'], status='done', progress=100), self.refresh()),
                      DONE, row_bg)

        if g['status'] == 'active':
            self._btn(btn_f, "⏸ Пауза",
                      lambda g=g: (db.update_goal(g['id'], status='paused'), self.refresh()),
                      STREAK, row_bg)
        elif g['status'] == 'paused':
            self._btn(btn_f, "▶ Відновити",
                      lambda g=g: (db.update_goal(g['id'], status='active'), self.refresh()),
                      ACCENT, row_bg)

        self._btn(btn_f, "🗑", lambda g=g: self._delete(g), FAIL, row_bg, side="right")

    def _btn(self, parent, text, cmd, color, row_bg, side="left"):
        b = tk.Label(parent, text=text, bg=_hex_fade(color,0.15), fg=color,
                     font=FONT_MONO, cursor="hand2", padx=10, pady=5)
        b.pack(side=side, padx=3)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=_hex_fade(color,0.3)))
        b.bind("<Leave>", lambda e: b.configure(bg=_hex_fade(color,0.15)))

    def _show_dialog(self, goal):
        win = tk.Toplevel(self)
        win.title("Редагувати ціль" if goal else "Нова ціль")
        win.configure(bg=SURFACE)
        win.geometry("460x440")
        win.resizable(False, False)
        win.grab_set()

        hdr = tk.Frame(win, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr, text="Нова ціль" if not goal else "Редагувати ціль",
                 bg=SURFACE, fg=TEXT, font=FONT_TITLE).pack(anchor="w")

        f = tk.Frame(win, bg=SURFACE, padx=24)
        f.pack(fill="x", pady=12)

        _, title_var = labeled_entry(f, "Назва *", bg=SURFACE, width=38)
        if goal: title_var.set(goal['title'])
        f.winfo_children()[-1].pack(fill="x", pady=(0,10))

        tk.Label(f, text="Опис", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        desc_txt = tk.Text(f, height=3, bg=SURFACE2, fg=TEXT, font=FONT_MAIN,
                           relief="flat", insertbackground=TEXT, wrap="word",
                           highlightthickness=1, highlightbackground=BORDER,
                           highlightcolor=ACCENT, bd=6)
        desc_txt.pack(fill="x", pady=(3,10))
        if goal and goal.get('description'): desc_txt.insert("1.0", goal['description'])

        cat_var = tk.StringVar(value=goal.get('category','personal') if goal else 'personal')
        tk.Label(f, text="Категорія", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        ttk.Combobox(f, textvariable=cat_var,
                     values=[v for v,_ in GOAL_CATEGORIES],
                     state="readonly", width=24).pack(anchor="w", pady=(3,10))

        _, dl_var = labeled_entry(f, "Дедлайн (РРРР-ММ-ДД)", bg=SURFACE, width=16)
        if goal and goal.get('deadline'): dl_var.set(goal['deadline'])
        f.winfo_children()[-1].pack(anchor="w")

        def save():
            t = title_var.get().strip()
            if not t:
                messagebox.showwarning("Помилка", "Введіть назву!", parent=win)
                return
            d_desc = desc_txt.get("1.0","end-1c").strip()
            dl = dl_var.get().strip() or None
            if goal:
                db.update_goal(goal['id'], title=t, description=d_desc,
                               category=cat_var.get(), deadline=dl)
            else:
                db.add_goal(t, d_desc, cat_var.get(), dl)
            win.destroy()
            self.refresh()

        save_btn = tk.Label(win, text="💾  Зберегти", bg=_hex_fade(ACCENT,0.2),
                            fg=ACCENT_L, font=FONT_BOLD, cursor="hand2", padx=20, pady=12)
        save_btn.pack(fill="x", padx=24, pady=16)
        save_btn.bind("<Button-1>", lambda e: save())
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.35)))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.2)))

    def _delete(self, goal):
        if messagebox.askyesno("Видалити?", f"Видалити ціль '{goal['title']}'?"):
            db.delete_goal(goal['id'])
            self.refresh()
