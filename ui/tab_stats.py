"""
SelfMaster - Statistics Tab
Charts and analytics using matplotlib embedded in tkinter.
"""
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from .theme import *
from .widgets import *
from db import queries as Q


class StatsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._matplotlib_ok = False
        self._try_import_matplotlib()
        self._build()

    def _try_import_matplotlib(self):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self._plt = plt
            self._mpatches = mpatches
            self._FigureCanvasTkAgg = FigureCanvasTkAgg
            self._matplotlib_ok = True
        except ImportError:
            self._matplotlib_ok = False

    def _build(self):
        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True)

        # Refresh button
        top = tk.Frame(self._scroll, bg=BG)
        top.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(top, text="СТАТИСТИКА ТА АНАЛІТИКА", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(top, text="⟳ Оновити", command=self.refresh,
                  bg=SURFACE2, fg=ACCENT3, font=FONT_MONO,
                  relief="flat", cursor="hand2").pack(side="right")

        self._content = tk.Frame(self._scroll, bg=BG)
        self._content.pack(fill="both", expand=True, padx=20)

        self.refresh()

    def refresh(self):
        for w in self._content.winfo_children():
            w.destroy()

        self._build_overall_stats()
        self._build_weekly_chart()
        self._build_habit_comparison()
        self._build_ideal_radar()
        self._build_mood_chart()
        self._build_top_habits()

    def _build_overall_stats(self):
        stats = Q.get_overall_stats()
        monthly = Q.get_monthly_stats(date.today().year, date.today().month)

        frame = tk.Frame(self._content, bg=BG)
        frame.pack(fill="x", pady=(0, 16))

        items = [
            ("Всього логів", str(stats['total']), "за весь час", ACCENT),
            ("Виконано", str(stats['done']), "всього", DONE),
            ("% успіху", f"{stats['pct']}%", "загальний", ACCENT2),
            ("Днів у трекері", str(stats['days_tracked']), "унікальних днів", ACCENT3),
            ("Звичок цього місяця", str(len(monthly)), "активних", STREAK),
        ]
        for label, val, sub, color in items:
            f = tk.Frame(frame, bg=SURFACE, padx=14, pady=10)
            f.pack(side="left", padx=(0, 8))
            tk.Frame(f, bg=color, height=2).pack(fill="x")
            tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 8)).pack(anchor="w", pady=(4, 0))
            tk.Label(f, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI", 20, "bold")).pack(anchor="w")
            tk.Label(f, text=sub, bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 8)).pack(anchor="w")

    def _build_weekly_chart(self):
        weekly = Q.get_weekly_data(12)
        if not weekly:
            return

        if self._matplotlib_ok:
            self._chart_weekly_matplotlib(weekly)
        else:
            self._chart_weekly_canvas(weekly)

    def _chart_weekly_matplotlib(self, weekly):
        plt = self._plt
        fig, ax = plt.subplots(figsize=(10, 2.8))
        fig.patch.set_facecolor(SURFACE)
        ax.set_facecolor(SURFACE)

        labels = [w['label'] for w in weekly]
        values = [w['pct'] for w in weekly]
        colors = [DONE if v >= 70 else STREAK if v >= 40 else FAIL for v in values]

        bars = ax.bar(labels, values, color=colors, width=0.6, zorder=2)
        ax.set_ylim(0, 100)
        ax.axhline(y=70, color=DONE, linestyle='--', alpha=0.3, linewidth=1)
        ax.set_ylabel('%', color=TEXT_DIM, fontsize=9)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        ax.spines['bottom'].set_color(BORDER)
        ax.spines['left'].set_color(BORDER)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', color=BORDER, alpha=0.5, zorder=1)

        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f"{val}%", ha='center', va='bottom',
                        color=TEXT_DIM, fontsize=7)

        ax.set_title("Тижневий % виконання звичок", color=TEXT, fontsize=10, pad=8)
        fig.tight_layout()

        self._embed_figure(fig, "ТИЖНЕВА АКТИВНІСТЬ")

    def _chart_weekly_canvas(self, weekly):
        """Fallback ASCII-style bar chart without matplotlib."""
        section = self._make_section("ТИЖНЕВА АКТИВНІСТЬ", ACCENT)
        values = [w['pct'] for w in weekly]
        max_v = max(values) if values else 100

        chart = tk.Frame(section, bg=SURFACE)
        chart.pack(fill="x", padx=14, pady=8)

        max_h = 80
        for w_data in weekly:
            col = tk.Frame(chart, bg=SURFACE)
            col.pack(side="left", expand=True)

            val = w_data['pct']
            bar_h = int(val / 100 * max_h) if val > 0 else 2
            color = DONE if val >= 70 else STREAK if val >= 40 else FAIL

            space = tk.Frame(col, bg=SURFACE, height=max_h - bar_h)
            space.pack()
            bar = tk.Frame(col, bg=color, height=bar_h, width=16)
            bar.pack()
            tk.Label(col, text=f"{val}%", bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 6)).pack()
            tk.Label(col, text=w_data['label'], bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 6)).pack()

    def _build_habit_comparison(self):
        monthly = Q.get_monthly_stats(date.today().year, date.today().month)
        if not monthly:
            return

        section = self._make_section("ПОРІВНЯННЯ ЗВИЧОК (ПОТОЧНИЙ МІСЯЦЬ)", ACCENT3)

        for h in sorted(monthly, key=lambda x: -x['pct']):
            row = tk.Frame(section, bg=SURFACE, padx=14, pady=5)
            row.pack(fill="x")

            # Name
            tk.Label(row, text=f"{h['emoji']} {h['name']}",
                     bg=SURFACE, fg=TEXT, font=FONT_MAIN, width=22, anchor="w").pack(side="left")

            # Progress bar
            bar_frame = tk.Frame(row, bg=BORDER, height=8, width=200)
            bar_frame.pack(side="left", padx=8)
            bar_frame.pack_propagate(False)

            pct = h['pct']
            color = DONE if pct >= 70 else STREAK if pct >= 40 else FAIL
            fill_w = int(200 * pct / 100)
            if fill_w > 0:
                bar = tk.Frame(bar_frame, bg=color, height=8, width=fill_w)
                bar.place(x=0, y=0)

            # Stats
            tk.Label(row, text=f"{pct}%", bg=SURFACE, fg=color,
                     font=("Consolas", 9, "bold"), width=5).pack(side="left")
            tk.Label(row, text=f"{h['done']}/{h['logged']}",
                     bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO, width=8).pack(side="left")
            if h['cur_streak'] > 0:
                tk.Label(row, text=f"🔥{h['cur_streak']}",
                         bg=SURFACE, fg=STREAK, font=FONT_MONO).pack(side="left")

    def _build_ideal_radar(self):
        cat_stats = Q.get_ideal_category_stats(30)
        if not cat_stats:
            return

        section = self._make_section("ІДЕАЛЬНА ЛЮДИНА — ЗА КАТЕГОРІЯМИ (30 ДНІВ)", ACCENT2)

        for row_data in cat_stats:
            cat = row_data['category']
            avg = row_data['avg_score'] or 0
            color = CATEGORY_COLORS.get(cat, ACCENT3)
            label = CATEGORY_LABELS.get(cat, cat)

            row = tk.Frame(section, bg=SURFACE, padx=14, pady=5)
            row.pack(fill="x")

            tk.Label(row, text=label, bg=SURFACE, fg=TEXT,
                     font=FONT_MAIN, width=16, anchor="w").pack(side="left")

            # Bar (max 5)
            bar_w = 160
            bar_frame = tk.Frame(row, bg=BORDER, height=8, width=bar_w)
            bar_frame.pack(side="left", padx=8)
            bar_frame.pack_propagate(False)
            fill = int(bar_w * avg / 5)
            if fill > 0:
                tk.Frame(bar_frame, bg=color, height=8, width=fill).place(x=0, y=0)

            # Stars
            stars = "●" * int(round(avg)) + "○" * (5 - int(round(avg)))
            tk.Label(row, text=stars, bg=SURFACE, fg=color,
                     font=("Consolas", 9)).pack(side="left", padx=4)
            tk.Label(row, text=f"{avg:.1f}/5",
                     bg=SURFACE, fg=color, font=("Consolas", 9)).pack(side="left")

    def _build_mood_chart(self):
        mood_data = Q.get_mood_data(30)
        if len(mood_data) < 2:
            return

        if self._matplotlib_ok:
            self._chart_mood_matplotlib(mood_data)
        else:
            self._chart_mood_simple(mood_data)

    def _chart_mood_matplotlib(self, mood_data):
        plt = self._plt
        fig, ax = plt.subplots(figsize=(10, 2.5))
        fig.patch.set_facecolor(SURFACE)
        ax.set_facecolor(SURFACE)

        dates = [d['entry_date'] for d in mood_data]
        moods = [d['mood'] for d in mood_data]
        energies = [d['energy'] for d in mood_data]

        xs = range(len(dates))
        ax.plot(xs, moods, color=ACCENT2, linewidth=2, marker='o',
                markersize=4, label='Настрій', zorder=3)
        ax.plot(xs, energies, color=ACCENT3, linewidth=2, marker='s',
                markersize=4, label='Енергія', zorder=3)
        ax.fill_between(xs, moods, alpha=0.1, color=ACCENT2)
        ax.fill_between(xs, energies, alpha=0.1, color=ACCENT3)

        ax.set_ylim(0.5, 5.5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['😞', '😕', '😐', '😊', '😄'])
        ax.set_xticks(xs[::3])
        ax.set_xticklabels([dates[i].replace(str(date.today().year)+'-', '') for i in xs[::3]],
                           rotation=30, fontsize=7)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for sp in ax.spines.values():
            sp.set_color(BORDER)
        ax.grid(alpha=0.2, color=BORDER)
        ax.legend(facecolor=SURFACE, edgecolor=BORDER,
                  labelcolor=TEXT, fontsize=8)
        ax.set_title("Настрій та Енергія (30 днів)", color=TEXT, fontsize=10, pad=8)
        fig.tight_layout()

        self._embed_figure(fig, "ДИНАМІКА НАСТРОЮ")

    def _chart_mood_simple(self, mood_data):
        section = self._make_section("ДИНАМІКА НАСТРОЮ", ACCENT2)
        tk.Label(section, text="Встановіть matplotlib для графіків: pip install matplotlib",
                 bg=SURFACE, fg=TEXT_DIM, font=FONT_MONO).pack(padx=14, pady=8)

        row = tk.Frame(section, bg=SURFACE)
        row.pack(fill="x", padx=14, pady=4)
        for d in mood_data[-15:]:
            col = tk.Frame(row, bg=SURFACE)
            col.pack(side="left", expand=True)
            em = MOOD_LABELS.get(d['mood'], {})
            em_text = MOOD_LABELS.get(d['mood'], "😐").split()[0]
            tk.Label(col, text=em_text, bg=SURFACE, font=("Segoe UI", 10)).pack()
            dt = d['entry_date'][-5:]
            tk.Label(col, text=dt, bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas", 6)).pack()

    def _build_top_habits(self):
        monthly = Q.get_monthly_stats(date.today().year, date.today().month)
        if not monthly:
            return

        section = self._make_section("ТОП ЗВИЧОК МІСЯЦЯ", STREAK)

        cols = tk.Frame(section, bg=SURFACE, padx=14, pady=8)
        cols.pack(fill="x")

        # Best habits
        left = tk.Frame(cols, bg=SURFACE)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="🏆 Найкращі", bg=SURFACE, fg=DONE,
                 font=FONT_BOLD).pack(anchor="w", pady=(0, 6))

        best = sorted([h for h in monthly if h['logged'] >= 3], key=lambda x: -x['pct'])[:5]
        for h in best:
            row = tk.Frame(left, bg=SURFACE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{h['emoji']} {h['name']}",
                     bg=SURFACE, fg=TEXT, font=FONT_MAIN, width=20, anchor="w").pack(side="left")
            tk.Label(row, text=f"{h['pct']}%",
                     bg=SURFACE, fg=DONE, font=("Consolas", 9, "bold")).pack(side="left")

        # Needs work
        right = tk.Frame(cols, bg=SURFACE)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="⚠️ Потребують уваги", bg=SURFACE, fg=FAIL,
                 font=FONT_BOLD).pack(anchor="w", pady=(0, 6))

        worst = sorted([h for h in monthly if h['logged'] >= 3], key=lambda x: x['pct'])[:5]
        for h in worst:
            row = tk.Frame(right, bg=SURFACE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{h['emoji']} {h['name']}",
                     bg=SURFACE, fg=TEXT, font=FONT_MAIN, width=20, anchor="w").pack(side="left")
            tk.Label(row, text=f"{h['pct']}%",
                     bg=SURFACE, fg=FAIL, font=("Consolas", 9, "bold")).pack(side="left")

    def _make_section(self, title, color):
        f = tk.Frame(self._content, bg=SURFACE, pady=0)
        f.pack(fill="x", pady=(0, 12))
        tk.Frame(f, bg=color, height=2).pack(fill="x")
        hdr = tk.Frame(f, bg=SURFACE, padx=14, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas", 9)).pack(anchor="w")
        return f

    def _embed_figure(self, fig, title):
        section = self._make_section(title, ACCENT)
        canvas = self._FigureCanvasTkAgg(fig, master=section)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=14, pady=(0, 8))
        self._plt.close(fig)
