"""SelfMaster — Habits Tab"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from ui import *
from ui.theme import *
from ui.widgets import scrollable_frame, hscrollable_frame, card, section_header, _hex_fade, labeled_entry
from db import queries as db

HABIT_TYPES = [("toggle","✅ Так/Ні"), ("number","🔢 Числове")]
CATEGORIES = [("health","❤️ Здоров'я"),("mind","🧠 Розум"),("physical","💪 Фізичне"),
              ("social","🤝 Соціальне"),("financial","💰 Фінанси"),("other","📌 Інше")]
EMOJIS = ["💪","📚","🧘","💧","🚬","😴","🚿","📵","🏃","🥗","☀️","🎯","✍️","🎨","🎵","🏋️",
          "🚴","🧗","🤸","🦷","💊","🍎","🍵","🥤","📱","💻","🎮","📺","💤","😊","⭐","🔥"]
PRESET_COLORS = [ACCENT, ACCENT2, ACCENT3, ACCENT4, DONE, FAIL, STREAK, "#f97316", "#14b8a6"]


class HabitsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr, text="КЕРУВАННЯ ЗВИЧКАМИ", bg=SURFACE, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")
        add_btn = tk.Label(hdr, text="＋  Нова звичка", bg=_hex_fade(ACCENT,0.2),
                           fg=ACCENT_L, font=FONT_BOLD, cursor="hand2",
                           padx=14, pady=8)
        add_btn.pack(side="right")
        add_btn.bind("<Button-1>", lambda e: self._show_dialog(None))
        add_btn.bind("<Enter>", lambda e: add_btn.configure(bg=_hex_fade(ACCENT,0.3)))
        add_btn.bind("<Leave>", lambda e: add_btn.configure(bg=_hex_fade(ACCENT,0.2)))

        # Tip
        tip = tk.Frame(self, bg=SURFACE2, padx=20, pady=10)
        tip.pack(fill="x", padx=20, pady=(12,0))
        tk.Label(tip, text="💡  Починай з 3–5 ключових звичок. Краще менше, але стабільно.",
                 bg=SURFACE2, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=12)
        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        habits = db.get_habits(active_only=False)
        active = [h for h in habits if h['is_active']]
        inactive = [h for h in habits if not h['is_active']]

        if not habits:
            tk.Label(self._scroll, text="Немає звичок. Натисніть '+ Нова звичка'.",
                     bg=BG, fg=TEXT_DIM, font=FONT_MAIN).pack(pady=40)
            return

        if active: self._build_group("АКТИВНІ ЗВИЧКИ", active, ACCENT)
        if inactive: self._build_group("АРХІВ", inactive, TEXT_DIM)

    def _build_group(self, title, habits, color):
        section_header(self._scroll, title, color)
        for i, h in enumerate(habits):
            self._build_habit_row(h, i, color)

    def _build_habit_row(self, h, i, group_color):
        row_bg = SURFACE if i % 2 == 0 else SURFACE2
        row = tk.Frame(self._scroll, bg=row_bg, padx=16, pady=12)
        row.pack(fill="x")

        # Accent left bar
        habit_color = h.get('color', ACCENT)
        tk.Frame(row, bg=habit_color, width=3, height=36).pack(side="left", padx=(0,12))

        # Emoji
        tk.Label(row, text=h['emoji'], bg=row_bg,
                 font=("Segoe UI", 17)).pack(side="left", padx=(0,10))

        # Info
        info = tk.Frame(row, bg=row_bg)
        info.pack(side="left", fill="x", expand=True)

        tk.Label(info, text=h['name'], bg=row_bg, fg=TEXT,
                 font=FONT_BOLD, anchor="w").pack(anchor="w")

        meta = []
        meta.append("Так/Ні" if h['type']=='toggle' else "Числове")
        if h.get('unit'): meta.append(f"одиниця: {h['unit']}")
        if h.get('goal_value') is not None: meta.append(f"ціль: {h['goal_value']}")
        if h.get('is_negative'): meta.append("хочу зменшити")
        cat_lbl = dict(CATEGORIES).get(h.get('category','other'), h.get('category',''))
        meta.append(cat_lbl)
        tk.Label(info, text="  ·  ".join(meta), bg=row_bg,
                 fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")

        cur_s, best_s = db.get_habit_streak(h['id'])
        if cur_s > 0 or best_s > 0:
            tk.Label(info, text=f"🔥 {cur_s} поточний  ·  рекорд: {best_s}",
                     bg=row_bg, fg=STREAK, font=FONT_MONO).pack(anchor="w")

        # Buttons
        btn_f = tk.Frame(row, bg=row_bg)
        btn_f.pack(side="right")

        self._btn(btn_f, "✎", lambda h=h: self._show_dialog(h), ACCENT3)
        if h['is_active']:
            self._btn(btn_f, "📦 Архів", lambda h=h: (db.update_habit(h['id'],is_active=0), self.refresh()), TEXT_DIM)
        else:
            self._btn(btn_f, "♻ Відновити", lambda h=h: (db.update_habit(h['id'],is_active=1), self.refresh()), DONE)
        self._btn(btn_f, "🗑", lambda h=h: self._delete(h), FAIL)

    def _btn(self, parent, text, cmd, color):
        b = tk.Label(parent, text=text, bg=SURFACE3, fg=color,
                     font=FONT_MONO, cursor="hand2", padx=8, pady=4)
        b.pack(side="left", padx=2)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=_hex_fade(color,0.2)))
        b.bind("<Leave>", lambda e: b.configure(bg=SURFACE3))

    def _show_dialog(self, habit):
        win = tk.Toplevel(self)
        win.title("Редагувати звичку" if habit else "Нова звичка")
        win.configure(bg=SURFACE)
        win.geometry("480x600")
        win.resizable(False, False)
        win.grab_set()

        # Header
        hdr_f = tk.Frame(win, bg=SURFACE, padx=24, pady=16)
        hdr_f.pack(fill="x")
        tk.Frame(hdr_f, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr_f, text="Нова звичка" if not habit else "Редагувати звичку",
                 bg=SURFACE, fg=TEXT, font=FONT_TITLE).pack(anchor="w")

        scroll_o, f = scrollable_frame(win, bg=SURFACE)
        scroll_o.pack(fill="both", expand=True)
        f_inner = tk.Frame(f, bg=SURFACE, padx=24)
        f_inner.pack(fill="x", pady=8)

        # Name
        _, name_var = labeled_entry(f_inner, "Назва звички *", bg=SURFACE, width=36)
        if habit: name_var.set(habit['name'])
        f_inner.winfo_children()[-1].pack(fill="x", pady=(0,14))

        # Emoji
        tk.Label(f_inner, text="Іконка", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        emoji_row = tk.Frame(f_inner, bg=SURFACE)
        emoji_row.pack(fill="x", pady=(3,14))
        emoji_var = tk.StringVar(value=habit['emoji'] if habit else "⭐")
        emoji_preview = tk.Label(emoji_row, textvariable=emoji_var, bg=SURFACE2,
                                  font=("Segoe UI", 20), width=3, pady=4)
        emoji_preview.pack(side="left", padx=(0,10))
        grid = tk.Frame(emoji_row, bg=SURFACE)
        grid.pack(side="left")
        for j, em in enumerate(EMOJIS):
            b = tk.Label(grid, text=em, bg=SURFACE, font=("Segoe UI", 12), cursor="hand2")
            b.grid(row=j//11, column=j%11, padx=1, pady=1)
            b.bind("<Button-1>", lambda e, em=em: emoji_var.set(em))

        # Type
        tk.Label(f_inner, text="Тип", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w", pady=(0,4))
        type_var = tk.StringVar(value=habit['type'] if habit else "toggle")
        type_f = tk.Frame(f_inner, bg=SURFACE)
        type_f.pack(anchor="w", pady=(0,14))
        for val, lbl in HABIT_TYPES:
            btn_bg = _hex_fade(ACCENT, 0.25) if type_var.get()==val else SURFACE2
            rb = tk.Label(type_f, text=lbl, bg=btn_bg, fg=TEXT,
                          font=FONT_MONO, cursor="hand2", padx=10, pady=6)
            rb.pack(side="left", padx=(0,6))
            def _sel(v=val, b=rb):
                type_var.set(v)
                for c in type_f.winfo_children():
                    c.configure(bg=SURFACE2)
                b.configure(bg=_hex_fade(ACCENT, 0.25))
            rb.bind("<Button-1>", lambda e, fn=_sel: fn())

        # Number fields
        num_f = tk.Frame(f_inner, bg=SURFACE)
        num_f.pack(fill="x", pady=(0,14))
        _, unit_var = labeled_entry(num_f, "Одиниця (стор., хв., кг...)", bg=SURFACE, width=20)
        if habit: unit_var.set(habit.get('unit') or "")
        num_f.winfo_children()[-1].pack(anchor="w", pady=(0,8))

        _, goal_var = labeled_entry(num_f, "Денна ціль", bg=SURFACE, width=10)
        if habit: goal_var.set(str(habit.get('goal_value') or ""))
        num_f.winfo_children()[-1].pack(anchor="w", pady=(0,8))

        is_neg = tk.BooleanVar(value=bool(habit.get('is_negative') if habit else False))
        neg_cb = tk.Checkbutton(num_f, text="Хочу ЗМЕНШИТИ цю метрику (куріння, соцмережі)",
                                variable=is_neg, bg=SURFACE, fg=TEXT_DIM,
                                selectcolor=SURFACE2, activebackground=SURFACE,
                                font=FONT_MONO)
        neg_cb.pack(anchor="w")

        # Category
        tk.Label(f_inner, text="Категорія", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_MONO).pack(anchor="w", pady=(0,4))
        cat_var = tk.StringVar(value=habit.get('category','health') if habit else 'health')
        cat_menu = ttk.Combobox(f_inner, textvariable=cat_var,
                                values=[v for v,_ in CATEGORIES],
                                state="readonly", width=22)
        cat_menu.pack(anchor="w", pady=(0,14))

        # Color
        color_var = tk.StringVar(value=habit.get('color', ACCENT) if habit else ACCENT)
        tk.Label(f_inner, text="Колір", bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
        color_row = tk.Frame(f_inner, bg=SURFACE)
        color_row.pack(anchor="w", pady=(3,0))
        color_preview = tk.Frame(color_row, bg=color_var.get(), width=36, height=24)
        color_preview.pack(side="left", padx=(0,8))

        def pick_color():
            c = colorchooser.askcolor(color=color_var.get(), title="Обери колір")
            if c[1]:
                color_var.set(c[1])
                color_preview.configure(bg=c[1])

        tk.Label(color_row, text="Обрати", bg=SURFACE2, fg=TEXT_MID,
                 font=FONT_MONO, cursor="hand2", padx=8, pady=4).pack(side="left", padx=(0,8))
        color_row.winfo_children()[-1].bind("<Button-1>", lambda e: pick_color())

        for pc in PRESET_COLORS:
            dot = tk.Frame(color_row, bg=pc, width=20, height=20, cursor="hand2")
            dot.pack(side="left", padx=2)
            dot.bind("<Button-1>", lambda e, c=pc: (color_var.set(c), color_preview.configure(bg=c)))

        # Save
        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Помилка", "Введіть назву звички!", parent=win)
                return
            try: goal = float(goal_var.get()) if goal_var.get().strip() else None
            except: goal = None

            if habit:
                db.update_habit(habit['id'],
                    name=name, emoji=emoji_var.get(), type=type_var.get(),
                    unit=unit_var.get().strip() or None, category=cat_var.get(),
                    goal_value=goal, is_negative=int(is_neg.get()), color=color_var.get())
            else:
                db.add_habit(name=name, emoji=emoji_var.get(), htype=type_var.get(),
                    unit=unit_var.get().strip() or None, category=cat_var.get(),
                    goal_value=goal, is_negative=int(is_neg.get()), color=color_var.get())
            win.destroy()
            self.refresh()

        save_btn = tk.Label(win, text="💾  Зберегти", bg=_hex_fade(ACCENT,0.2),
                            fg=ACCENT_L, font=FONT_BOLD, cursor="hand2",
                            padx=20, pady=12)
        save_btn.pack(fill="x", padx=24, pady=16)
        save_btn.bind("<Button-1>", lambda e: save())
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.35)))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=_hex_fade(ACCENT,0.2)))

    def _delete(self, habit):
        if messagebox.askyesno("Видалити?",
                               f"Видалити '{habit['name']}'?\nВсі дані буде втрачено!"):
            db.delete_habit(habit['id'])
            self.refresh()
