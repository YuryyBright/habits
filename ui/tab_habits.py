"""
SelfMaster - Habits Management Tab
Add, edit, reorder, delete habits.
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from .theme import *
from .widgets import *
from db import queries as Q


HABIT_TYPES = [
    ("toggle", "✅ Так/Ні — виконано або ні"),
    ("number", "🔢 Числове — кількість (стор., кг, хв...)"),
]

CATEGORIES = [
    ("health",   "❤️ Здоров'я"),
    ("mind",     "🧠 Розум"),
    ("physical", "💪 Фізичне"),
    ("social",   "🤝 Соціальне"),
    ("financial","💰 Фінанси"),
    ("other",    "📌 Інше"),
]

EMOJIS = ["💪","📚","🧘","💧","🚬","😴","🚿","📵","🏃","🥗","☀️","🎯","✍️","🎨","🎵","🏋️",
          "🚴","🧗","🤸","🦷","💊","🍎","🍵","🥤","📱","💻","🎮","📺","💤","😊"]


class HabitsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(16, 8))

        tk.Label(top, text="КЕРУВАННЯ ЗВИЧКАМИ", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(top, text="+ Нова звичка", command=self._show_add,
                  bg=ACCENT, fg=BG, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=12, pady=6).pack(side="right")

        # Tip card
        tip = tk.Frame(self, bg=SURFACE, padx=16, pady=10)
        tip.pack(fill="x", padx=20, pady=(0, 12))
        tk.Frame(tip, bg=ACCENT3, height=2).pack(fill="x")
        tk.Label(tip, text="💡 Починай з 3–5 ключових звичок. Краще менше, але стабільно.",
                 bg=SURFACE, fg=TEXT_DIM, font=FONT_MAIN).pack(anchor="w", pady=(6, 0))

        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20)

        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        habits = Q.get_habits(active_only=False)
        active = [h for h in habits if h['is_active']]
        inactive = [h for h in habits if not h['is_active']]

        if not habits:
            tk.Label(self._scroll, text="Немає звичок. Натисніть '+ Нова звичка'.",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=30)
            return

        if active:
            self._build_group("АКТИВНІ ЗВИЧКИ", active, ACCENT)
        if inactive:
            self._build_group("АРХІВ", inactive, TEXT_DIM)

    def _build_group(self, title, habits, color):
        # Header
        hdr = tk.Frame(self._scroll, bg=BG)
        hdr.pack(fill="x", pady=(8, 4))
        tk.Label(hdr, text=title, bg=BG, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(side="left")
        sep = tk.Frame(hdr, bg=BORDER, height=1)
        sep.pack(side="left", fill="x", expand=True, padx=(8, 0), pady=10)

        for i, h in enumerate(habits):
            row_bg = SURFACE if i % 2 == 0 else SURFACE2
            row = tk.Frame(self._scroll, bg=row_bg, padx=12, pady=8)
            row.pack(fill="x")

            # Color dot
            dot = tk.Frame(row, bg=h.get('color', color), width=4, height=36)
            dot.pack(side="left", padx=(0, 10))

            # Emoji + Name
            tk.Label(row, text=h['emoji'], bg=row_bg,
                     font=("Segoe UI", 16)).pack(side="left", padx=(0, 8))

            info = tk.Frame(row, bg=row_bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=h['name'], bg=row_bg, fg=TEXT,
                     font=FONT_BOLD, anchor="w").pack(anchor="w")

            # Meta info
            meta_parts = []
            type_labels = {"toggle": "Так/Ні", "number": "Числове"}
            meta_parts.append(type_labels.get(h['type'], h['type']))
            if h.get('unit'):
                meta_parts.append(f"одиниця: {h['unit']}")
            if h.get('goal_value') is not None:
                meta_parts.append(f"ціль: {h['goal_value']}")
            if h.get('is_negative'):
                meta_parts.append("хочу зменшити")
            cat_lbl = dict(CATEGORIES).get(h.get('category', 'other'), h.get('category', ''))
            meta_parts.append(cat_lbl)

            tk.Label(info, text="  •  ".join(meta_parts), bg=row_bg,
                     fg=TEXT_DIM, font=FONT_MONO, anchor="w").pack(anchor="w")

            # Stats
            cur_s, best_s = Q.get_habit_streak(h['id'])
            if cur_s > 0 or best_s > 0:
                tk.Label(info, text=f"🔥 Streak: {cur_s} (рекорд: {best_s})",
                         bg=row_bg, fg=STREAK, font=FONT_MONO).pack(anchor="w")

            # Buttons
            btn_f = tk.Frame(row, bg=row_bg)
            btn_f.pack(side="right")

            tk.Button(btn_f, text="✎ Редагувати",
                      command=lambda h=h: self._show_edit(h),
                      bg=SURFACE2, fg=ACCENT3, font=FONT_MONO,
                      relief="flat", cursor="hand2").pack(side="left", padx=2)

            if h['is_active']:
                tk.Button(btn_f, text="📦 Архів",
                          command=lambda h=h: self._archive(h),
                          bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO,
                          relief="flat", cursor="hand2").pack(side="left", padx=2)
            else:
                tk.Button(btn_f, text="♻️ Відновити",
                          command=lambda h=h: self._restore(h),
                          bg=SURFACE2, fg=ACCENT, font=FONT_MONO,
                          relief="flat", cursor="hand2").pack(side="left", padx=2)

            tk.Button(btn_f, text="🗑",
                      command=lambda h=h: self._delete(h),
                      bg=SURFACE2, fg=FAIL, font=FONT_MONO,
                      relief="flat", cursor="hand2").pack(side="left")

    def _show_add(self):
        self._show_dialog(None)

    def _show_edit(self, habit):
        self._show_dialog(habit)

    def _show_dialog(self, habit):
        win = tk.Toplevel()
        win.title("Редагувати звичку" if habit else "Нова звичка")
        win.configure(bg=SURFACE2)
        win.geometry("460x560")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Нова звичка" if not habit else "Редагувати звичку",
                 bg=SURFACE2, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(
            padx=20, pady=(16, 12), anchor="w")

        f = tk.Frame(win, bg=SURFACE2, padx=20)
        f.pack(fill="x")

        # Name
        _, name_var = labeled_entry(f, "Назва звички *", bg=SURFACE2, width=38)
        if habit:
            name_var.set(habit['name'])
        f.winfo_children()[-1].pack(fill="x", pady=(0, 10))

        # Emoji row
        tk.Label(f, text="Іконка", bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        emoji_row = tk.Frame(f, bg=SURFACE2)
        emoji_row.pack(fill="x", pady=(2, 10))

        emoji_var = tk.StringVar(value=habit['emoji'] if habit else "⭐")
        emoji_preview = tk.Label(emoji_row, textvariable=emoji_var, bg=SURFACE,
                                 font=("Segoe UI", 20), width=3)
        emoji_preview.pack(side="left", padx=(0, 8))

        emg = tk.Frame(emoji_row, bg=SURFACE2)
        emg.pack(side="left")
        for j, em in enumerate(EMOJIS):
            btn = tk.Label(emg, text=em, bg=SURFACE2, font=("Segoe UI", 11), cursor="hand2")
            btn.grid(row=j//10, column=j%10, padx=1, pady=1)
            btn.bind("<Button-1>", lambda e, em=em: emoji_var.set(em))

        # Type
        tk.Label(f, text="Тип", bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w", pady=(4, 0))
        type_var = tk.StringVar(value=habit['type'] if habit else "toggle")
        for val, lbl in HABIT_TYPES:
            tk.Radiobutton(f, text=lbl, variable=type_var, value=val,
                           bg=SURFACE2, fg=TEXT, selectcolor=SURFACE2,
                           activebackground=SURFACE2, font=FONT_MAIN).pack(anchor="w", pady=1)

        # Number fields (shown when type = number)
        num_frame = tk.Frame(f, bg=SURFACE2)
        num_frame.pack(fill="x", pady=(4, 0))

        _, unit_var = labeled_entry(num_frame, "Одиниця виміру (напр: стор., хв.)",
                                    bg=SURFACE2, width=20)
        if habit:
            unit_var.set(habit.get('unit') or "")
        num_frame.winfo_children()[-1].pack(anchor="w")

        _, goal_var = labeled_entry(num_frame, "Ціль (за день)", bg=SURFACE2, width=10)
        if habit:
            goal_var.set(str(habit.get('goal_value') or ""))
        num_frame.winfo_children()[-1].pack(anchor="w", pady=(6, 0))

        # Negative
        is_neg_var = tk.BooleanVar(value=bool(habit.get('is_negative') if habit else False))
        tk.Checkbutton(num_frame, text="Хочу ЗМЕНШИТИ цю метрику (напр. куріння)",
                       variable=is_neg_var, bg=SURFACE2, fg=TEXT_DIM,
                       selectcolor=SURFACE2, activebackground=SURFACE2,
                       font=FONT_MONO).pack(anchor="w", pady=4)

        # Category
        tk.Label(f, text="Категорія", bg=SURFACE2, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w", pady=(8, 2))
        cat_var = tk.StringVar(value=habit.get('category', 'health') if habit else 'health')
        cat_menu = ttk.Combobox(f, textvariable=cat_var,
                                values=[v for v, _ in CATEGORIES],
                                state="readonly", width=24)
        cat_menu.pack(anchor="w")

        # Color
        color_var = tk.StringVar(value=habit.get('color', ACCENT) if habit else ACCENT)
        tk.Label(f, text="Колір", bg=SURFACE2, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w", pady=(8, 2))
        color_row = tk.Frame(f, bg=SURFACE2)
        color_row.pack(anchor="w")
        color_preview = tk.Frame(color_row, bg=color_var.get(), width=32, height=22)
        color_preview.pack(side="left", padx=(0, 8))

        def pick_color():
            c = colorchooser.askcolor(color=color_var.get(), title="Обери колір")
            if c[1]:
                color_var.set(c[1])
                color_preview.configure(bg=c[1])

        tk.Button(color_row, text="Обрати колір", command=pick_color,
                  bg=SURFACE, fg=TEXT, font=FONT_MONO, relief="flat").pack(side="left")

        # Preset colors
        presets = [ACCENT, ACCENT2, ACCENT3, STREAK, FAIL, "#a78bfa", "#22c55e"]
        for pc in presets:
            btn = tk.Frame(color_row, bg=pc, width=18, height=18, cursor="hand2")
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, pc=pc: (color_var.set(pc), color_preview.configure(bg=pc)))

        # Save
        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Помилка", "Введіть назву звички!")
                return
            try:
                goal = float(goal_var.get()) if goal_var.get().strip() else None
            except:
                goal = None

            kwargs = dict(
                name=name, emoji=emoji_var.get(),
                htype=type_var.get(), unit=unit_var.get().strip() or None,
                category=cat_var.get(), goal_value=goal,
                is_negative=int(is_neg_var.get()), color=color_var.get()
            )
            if habit:
                Q.update_habit(habit['id'],
                               name=name, emoji=emoji_var.get(),
                               type=type_var.get(),
                               unit=unit_var.get().strip() or None,
                               category=cat_var.get(), goal_value=goal,
                               is_negative=int(is_neg_var.get()),
                               color=color_var.get())
            else:
                Q.add_habit(**kwargs)
            win.destroy()
            self.refresh()

        tk.Button(win, text="💾 Зберегти", command=save,
                  bg=ACCENT, fg=BG, font=FONT_BOLD, relief="flat",
                  cursor="hand2", padx=16, pady=8).pack(padx=20, pady=(12, 16))

    def _archive(self, habit):
        Q.update_habit(habit['id'], is_active=0)
        self.refresh()

    def _restore(self, habit):
        Q.update_habit(habit['id'], is_active=1)
        self.refresh()

    def _delete(self, habit):
        if messagebox.askyesno("Видалити?",
                               f"Видалити '{habit['name']}'?\nВсі дані буде втрачено!"):
            Q.delete_habit(habit['id'])
            self.refresh()
