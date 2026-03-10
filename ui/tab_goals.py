"""
SelfMaster - Goals Tab
Set and track personal goals.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from .theme import *
from .widgets import *
from db import queries as Q


GOAL_CATEGORIES = [
    ("health", "❤️ Здоров'я"), ("career", "💼 Кар'єра"),
    ("financial", "💰 Фінанси"), ("personal", "🌱 Особистий розвиток"),
    ("social", "🤝 Соціальне"), ("other", "📌 Інше"),
]


class GoalsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(16, 8))

        tk.Label(top, text="МОЇ ЦІЛІ", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(top, text="+ Нова ціль", command=self._show_add,
                  bg=ACCENT, fg=BG, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=12, pady=6).pack(side="right")

        # Filter
        filter_frame = tk.Frame(self, bg=BG)
        filter_frame.pack(fill="x", padx=20, pady=(0, 8))
        self._status_var = tk.StringVar(value="active")
        for val, lbl in [("active", "Активні"), ("done", "Виконані"), ("paused", "Пауза")]:
            tk.Radiobutton(filter_frame, text=lbl, variable=self._status_var,
                           value=val, bg=BG, fg=TEXT_DIM,
                           selectcolor=BG, activebackground=BG,
                           font=FONT_MONO, command=self.refresh).pack(side="left", padx=(0, 12))

        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20)

        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        goals = Q.get_goals(self._status_var.get())
        if not goals:
            tk.Label(self._scroll,
                     text="Немає цілей. Натисніть '+ Нова ціль' щоб почати!",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=30)
            return

        for i, g in enumerate(goals):
            self._build_goal_card(g, i)

    def _build_goal_card(self, g, i):
        row_bg = SURFACE if i % 2 == 0 else SURFACE2
        card = tk.Frame(self._scroll, bg=row_bg, padx=14, pady=12)
        card.pack(fill="x", pady=(0, 4))

        cat_color = dict([
            ("health", ACCENT), ("career", ACCENT3), ("financial", STREAK),
            ("personal", ACCENT2), ("social", "#a78bfa"), ("other", TEXT_DIM)
        ]).get(g['category'], ACCENT3)

        tk.Frame(card, bg=cat_color, height=2).pack(fill="x")

        # Header row
        hdr = tk.Frame(card, bg=row_bg)
        hdr.pack(fill="x", pady=(8, 4))

        tk.Label(hdr, text=g['title'], bg=row_bg, fg=TEXT,
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", fill="x", expand=True)

        status_colors = {"active": ACCENT, "done": DONE, "paused": STREAK}
        status_labels = {"active": "● Активна", "done": "✔ Виконано", "paused": "⏸ Пауза"}
        tk.Label(hdr, text=status_labels.get(g['status'], g['status']),
                 bg=row_bg, fg=status_colors.get(g['status'], TEXT_DIM),
                 font=FONT_MONO).pack(side="right")

        # Description
        if g.get('description'):
            tk.Label(card, text=g['description'], bg=row_bg, fg=TEXT_DIM,
                     font=FONT_MAIN, anchor="w", wraplength=600, justify="left").pack(
                anchor="w", pady=(0, 6))

        # Meta
        meta = tk.Frame(card, bg=row_bg)
        meta.pack(fill="x", pady=(0, 8))

        cat_lbl = dict(GOAL_CATEGORIES).get(g['category'], g['category'])
        tk.Label(meta, text=cat_lbl, bg=row_bg, fg=cat_color,
                 font=FONT_MONO).pack(side="left", padx=(0, 16))
        if g.get('deadline'):
            dl = g['deadline']
            try:
                dl_date = date.fromisoformat(dl)
                days_left = (dl_date - date.today()).days
                dl_color = FAIL if days_left < 7 else STREAK if days_left < 30 else TEXT_DIM
                tk.Label(meta, text=f"📅 {dl} ({days_left} днів)",
                         bg=row_bg, fg=dl_color, font=FONT_MONO).pack(side="left", padx=(0, 16))
            except:
                tk.Label(meta, text=f"📅 {dl}", bg=row_bg, fg=TEXT_DIM,
                         font=FONT_MONO).pack(side="left", padx=(0, 16))

        created = g.get('created_at', '')
        if created:
            tk.Label(meta, text=f"Створено: {created}", bg=row_bg, fg=TEXT_DIM,
                     font=FONT_MONO).pack(side="right")

        # Progress bar
        prog = g.get('progress', 0)
        prog_color = DONE if prog >= 100 else ACCENT3 if prog >= 50 else STREAK

        prog_row = tk.Frame(card, bg=row_bg)
        prog_row.pack(fill="x", pady=(0, 8))

        tk.Label(prog_row, text=f"Прогрес: {prog}%", bg=row_bg,
                 fg=prog_color, font=FONT_BOLD).pack(side="left", padx=(0, 12))

        bar_frame = tk.Frame(prog_row, bg=BORDER, height=8)
        bar_frame.pack(side="left", fill="x", expand=True)
        bar_frame.pack_propagate(False)
        if prog > 0:
            fill_f = tk.Frame(bar_frame, bg=prog_color, height=8)
            fill_f.place(relwidth=prog/100, relheight=1)

        # Progress slider
        prog_var = tk.IntVar(value=prog)

        def update_progress(val, gid=g['id']):
            Q.update_goal(gid, progress=int(float(val)))
            fill_f.place(relwidth=int(float(val))/100, relheight=1)

        scale = ttk.Scale(card, from_=0, to=100, orient="horizontal",
                          variable=prog_var, command=update_progress)
        scale.pack(fill="x")

        # Action buttons
        btn_f = tk.Frame(card, bg=row_bg)
        btn_f.pack(fill="x", pady=(8, 0))

        tk.Button(btn_f, text="✎ Редагувати",
                  command=lambda g=g: self._show_edit(g),
                  bg=SURFACE2, fg=ACCENT3, font=FONT_MONO,
                  relief="flat", cursor="hand2").pack(side="left", padx=(0, 4))

        if g['status'] != 'done':
            tk.Button(btn_f, text="✔ Виконано",
                      command=lambda g=g: (Q.update_goal(g['id'], status='done', progress=100), self.refresh()),
                      bg="#eafaf1", fg=DONE, font=FONT_MONO,
                      relief="flat", cursor="hand2").pack(side="left", padx=(0, 4))

        if g['status'] == 'active':
            tk.Button(btn_f, text="⏸ Пауза",
                      command=lambda g=g: (Q.update_goal(g['id'], status='paused'), self.refresh()),
                      bg=SURFACE2, fg=STREAK, font=FONT_MONO,
                      relief="flat", cursor="hand2").pack(side="left", padx=(0, 4))
        elif g['status'] == 'paused':
            tk.Button(btn_f, text="▶ Відновити",
                      command=lambda g=g: (Q.update_goal(g['id'], status='active'), self.refresh()),
                      bg=SURFACE2, fg=ACCENT, font=FONT_MONO,
                      relief="flat", cursor="hand2").pack(side="left", padx=(0, 4))

        tk.Button(btn_f, text="🗑",
                  command=lambda g=g: self._delete(g),
                  bg=SURFACE2, fg=FAIL, font=FONT_MONO,
                  relief="flat", cursor="hand2").pack(side="right")

    def _show_add(self):
        self._show_dialog(None)

    def _show_edit(self, goal):
        self._show_dialog(goal)

    def _show_dialog(self, goal):
        win = tk.Toplevel()
        win.title("Редагувати ціль" if goal else "Нова ціль")
        win.configure(bg=SURFACE2)
        win.geometry("440x420")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Нова ціль" if not goal else "Редагувати ціль",
                 bg=SURFACE2, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(
            padx=20, pady=(16, 12), anchor="w")

        f = tk.Frame(win, bg=SURFACE2, padx=20)
        f.pack(fill="x")

        _, title_var = labeled_entry(f, "Назва *", bg=SURFACE2, width=38)
        if goal:
            title_var.set(goal['title'])
        f.winfo_children()[-1].pack(fill="x", pady=(0, 10))

        tk.Label(f, text="Опис", bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        desc_txt = tk.Text(f, height=3, bg=SURFACE, fg=TEXT,
                           font=FONT_MAIN, relief="flat", insertbackground=TEXT,
                           wrap="word", highlightthickness=1,
                           highlightbackground=BORDER, highlightcolor=ACCENT3, bd=4)
        desc_txt.pack(fill="x", pady=(2, 10))
        if goal and goal.get('description'):
            desc_txt.insert("1.0", goal['description'])

        cat_var = tk.StringVar(value=goal.get('category', 'personal') if goal else 'personal')
        tk.Label(f, text="Категорія", bg=SURFACE2, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w")
        ttk.Combobox(f, textvariable=cat_var,
                     values=[v for v, _ in GOAL_CATEGORIES],
                     state="readonly", width=24).pack(anchor="w", pady=(2, 10))

        _, deadline_var = labeled_entry(f, "Дедлайн (РРРР-ММ-ДД)", bg=SURFACE2, width=16)
        if goal and goal.get('deadline'):
            deadline_var.set(goal['deadline'])
        f.winfo_children()[-1].pack(anchor="w")

        def save():
            t = title_var.get().strip()
            if not t:
                messagebox.showwarning("Помилка", "Введіть назву!")
                return
            d_desc = desc_txt.get("1.0", "end-1c").strip()
            dl = deadline_var.get().strip() or None
            if goal:
                Q.update_goal(goal['id'], title=t, description=d_desc,
                              category=cat_var.get(), deadline=dl)
            else:
                Q.add_goal(t, d_desc, cat_var.get(), dl)
            win.destroy()
            self.refresh()

        tk.Button(win, text="💾 Зберегти", command=save,
                  bg=ACCENT, fg=BG, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=16, pady=8).pack(padx=20, pady=12)

    def _delete(self, goal):
        if messagebox.askyesno("Видалити?", f"Видалити ціль '{goal['title']}'?"):
            Q.delete_goal(goal['id'])
            self.refresh()
