"""SelfMaster — Statistics Tab"""
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from ui import *
from ui.theme import *
from ui.widgets import scrollable_frame, hscrollable_frame, card, section_header, _hex_fade
from db import queries as db


class StatsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._mpl_ok = False
        self._try_matplotlib()
        self._build()

    def _try_matplotlib(self):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self._plt = plt
            self._FCA = FigureCanvasTkAgg
            self._mpl_ok = True
        except ImportError:
            pass

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(hdr, text="СТАТИСТИКА ТА АНАЛІТИКА", bg=SURFACE, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")
        ref_btn = tk.Label(hdr, text="⟳  Оновити", bg=SURFACE2, fg=TEXT_MID,
                           font=FONT_MONO, cursor="hand2", padx=10, pady=6)
        ref_btn.pack(side="right")
        ref_btn.bind("<Button-1>", lambda e: self.refresh())
        ref_btn.bind("<Enter>", lambda e: ref_btn.configure(bg=SURFACE3, fg=ACCENT_L))
        ref_btn.bind("<Leave>", lambda e: ref_btn.configure(bg=SURFACE2, fg=TEXT_MID))

        scroll_outer, self._scroll = scrollable_frame(self, bg=BG)
        scroll_outer.pack(fill="both", expand=True)

        self._content = tk.Frame(self._scroll, bg=BG)
        self._content.pack(fill="both", expand=True, padx=20, pady=12)

        self.refresh()

    def refresh(self):
        for w in self._content.winfo_children():
            w.destroy()
        self._build_summary()
        self._build_weekly()
        self._build_comparison()
        self._build_ideal_radar()
        self._build_mood_chart()
        self._build_top_bottom()

    def _section(self, title, color):
        f = tk.Frame(self._content, bg=SURFACE)
        f.pack(fill="x", pady=(0,12))
        tk.Frame(f, bg=color, height=2).pack(fill="x")
        hdr = tk.Frame(f, bg=SURFACE, padx=16, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas",9,"bold")).pack(anchor="w")
        return f

    def _build_summary(self):
        stats = db.get_overall_stats()
        monthly = db.get_monthly_stats(date.today().year, date.today().month)

        frame = tk.Frame(self._content, bg=BG)
        frame.pack(fill="x", pady=(0,16))

        for label, val, sub, color in [
            ("Всього логів", str(stats['total']), "за весь час", ACCENT),
            ("Виконано", str(stats['done']), "логів", DONE),
            ("% успіху", f"{stats['pct']}%", "загальний", ACCENT3),
            ("Днів у трекері", str(stats['days_tracked']), "унікальних", STREAK),
            ("Звичок цього місяця", str(len(monthly)), "активних", ACCENT2),
        ]:
            f = tk.Frame(frame, bg=SURFACE, padx=14, pady=12)
            f.pack(side="left", padx=(0,8))
            tk.Frame(f, bg=color, height=2).pack(fill="x")
            tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",8)).pack(anchor="w", pady=(6,2))
            tk.Label(f, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI",20,"bold")).pack(anchor="w")
            tk.Label(f, text=sub, bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",8)).pack(anchor="w")

    def _build_weekly(self):
        weekly = db.get_weekly_data(12)
        if not weekly: return

        if self._mpl_ok:
            self._weekly_matplotlib(weekly)
        else:
            self._weekly_canvas(weekly)

    def _weekly_matplotlib(self, weekly):
        plt = self._plt
        BG_C, SURF_C = BG, SURFACE
        fig, ax = plt.subplots(figsize=(10, 2.8))
        fig.patch.set_facecolor(SURF_C)
        ax.set_facecolor(SURF_C)

        labels = [w['label'] for w in weekly]
        values = [w['pct'] for w in weekly]
        colors = [DONE if v>=70 else STREAK if v>=40 else FAIL for v in values]

        bars = ax.bar(labels, values, color=colors, width=0.6, zorder=2, alpha=0.85)
        ax.set_ylim(0, 110)
        ax.axhline(y=70, color=DONE, linestyle='--', alpha=0.25, linewidth=1)
        ax.set_ylabel('%', color=TEXT_DIM, fontsize=9)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for sp in ['bottom','left','top','right']:
            ax.spines[sp].set_color(BORDER if sp in ['bottom','left'] else 'none')
        ax.grid(axis='y', color=BORDER, alpha=0.4, zorder=1)
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                        f"{val}%", ha='center', va='bottom', color=TEXT_DIM, fontsize=7)
        ax.set_title("% виконання звичок по тижнях", color=TEXT_MID, fontsize=10, pad=8)
        fig.tight_layout()
        self._embed_fig(fig, "ТИЖНЕВА АКТИВНІСТЬ", ACCENT)

    def _weekly_canvas(self, weekly):
        section = self._section("ТИЖНЕВА АКТИВНІСТЬ", ACCENT)
        chart = tk.Frame(section, bg=SURFACE, padx=14, pady=8)
        chart.pack(fill="x")
        max_h = 80
        for w_data in weekly:
            col = tk.Frame(chart, bg=SURFACE)
            col.pack(side="left", expand=True)
            val = w_data['pct']
            bar_h = max(2, int(val/100*max_h))
            color = DONE if val>=70 else STREAK if val>=40 else FAIL
            tk.Frame(col, bg=SURFACE, height=max_h-bar_h).pack()
            tk.Frame(col, bg=color, height=bar_h, width=14).pack()
            tk.Label(col, text=f"{val}%", bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",6)).pack()
            tk.Label(col, text=w_data['label'], bg=SURFACE, fg=TEXT_DIM,
                     font=("Consolas",6)).pack()

    def _build_comparison(self):
        monthly = db.get_monthly_stats(date.today().year, date.today().month)
        if not monthly: return
        section = self._section("ПОРІВНЯННЯ ЗВИЧОК (ПОТОЧНИЙ МІСЯЦЬ)", ACCENT3)

        for h in sorted(monthly, key=lambda x: -x['pct']):
            row = tk.Frame(section, bg=SURFACE, padx=16, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=f"{h['emoji']} {h['name']}", bg=SURFACE,
                     fg=TEXT, font=FONT_MONO, width=24, anchor="w").pack(side="left")

            # Progress bar
            bar_outer = tk.Frame(row, bg=SURFACE3, height=8, width=200)
            bar_outer.pack(side="left", padx=8)
            bar_outer.pack_propagate(False)
            pct = h['pct']
            color = DONE if pct>=70 else STREAK if pct>=40 else FAIL
            fill_w = int(200*pct/100)
            if fill_w > 0:
                tk.Frame(bar_outer, bg=color, height=8, width=fill_w).place(x=0,y=0)

            tk.Label(row, text=f"{pct}%", bg=SURFACE, fg=color,
                     font=("Consolas",9,"bold"), width=5).pack(side="left")
            tk.Label(row, text=f"{h['done']}/{h['logged']}", bg=SURFACE,
                     fg=TEXT_DIM, font=FONT_MONO, width=8).pack(side="left")
            if h.get('cur_streak',0) > 0:
                tk.Label(row, text=f"🔥{h['cur_streak']}", bg=SURFACE,
                         fg=STREAK, font=FONT_MONO).pack(side="left")

    def _build_ideal_radar(self):
        cat_stats = db.get_ideal_category_stats(30)
        if not cat_stats: return
        section = self._section("ІДЕАЛЬНА ЛЮДИНА — ЗА КАТЕГОРІЯМИ (30 ДНІВ)", ACCENT2)

        for row_data in cat_stats:
            cat = row_data['category']
            avg = row_data['avg_score'] or 0
            color = CATEGORY_COLORS.get(cat, ACCENT3)
            label = CATEGORY_LABELS.get(cat, cat)

            row = tk.Frame(section, bg=SURFACE, padx=16, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=label, bg=SURFACE, fg=TEXT,
                     font=FONT_MONO, width=18, anchor="w").pack(side="left")

            bar_w = 160
            bar_outer = tk.Frame(row, bg=SURFACE3, height=8, width=bar_w)
            bar_outer.pack(side="left", padx=8)
            bar_outer.pack_propagate(False)
            fill = int(bar_w * avg / 5)
            if fill > 0:
                tk.Frame(bar_outer, bg=color, height=8, width=fill).place(x=0,y=0)

            stars = "●"*int(round(avg)) + "○"*(5-int(round(avg)))
            tk.Label(row, text=stars, bg=SURFACE, fg=color,
                     font=("Consolas",10)).pack(side="left", padx=4)
            tk.Label(row, text=f"{avg:.1f}/5", bg=SURFACE, fg=color,
                     font=("Consolas",9)).pack(side="left")

    def _build_mood_chart(self):
        mood_data = db.get_mood_data(30)
        if len(mood_data) < 2: return

        if self._mpl_ok:
            self._mood_matplotlib(mood_data)
        else:
            self._mood_simple(mood_data)

    def _mood_matplotlib(self, mood_data):
        plt = self._plt
        fig, ax = plt.subplots(figsize=(10, 2.5))
        fig.patch.set_facecolor(SURFACE)
        ax.set_facecolor(SURFACE)

        dates = [d['entry_date'] for d in mood_data]
        moods = [d['mood'] for d in mood_data]
        energies = [d['energy'] for d in mood_data]
        xs = range(len(dates))

        ax.plot(xs, moods, color=ACCENT2, lw=2, marker='o', markersize=4, label='Настрій', zorder=3)
        ax.plot(xs, energies, color=ACCENT3, lw=2, marker='s', markersize=4, label='Енергія', zorder=3)
        ax.fill_between(xs, moods, alpha=0.08, color=ACCENT2)
        ax.fill_between(xs, energies, alpha=0.08, color=ACCENT3)

        ax.set_ylim(0.5, 5.5)
        ax.set_yticks([1,2,3,4,5])
        ax.set_yticklabels(['😞','😕','😐','😊','😄'])
        ax.set_xticks(xs[::3])
        ax.set_xticklabels([dates[i][-5:] for i in xs[::3]], rotation=30, fontsize=7)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for sp in ax.spines.values(): sp.set_color(BORDER)
        ax.grid(alpha=0.15, color=BORDER)
        ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT, fontsize=8)
        ax.set_title("Настрій та Енергія (30 днів)", color=TEXT_MID, fontsize=10, pad=8)
        fig.tight_layout()
        self._embed_fig(fig, "ДИНАМІКА НАСТРОЮ", ACCENT2)

    def _mood_simple(self, mood_data):
        section = self._section("ДИНАМІКА НАСТРОЮ", ACCENT2)
        row = tk.Frame(section, bg=SURFACE, padx=16)
        row.pack(fill="x", pady=4)
        for d in mood_data[-20:]:
            col = tk.Frame(row, bg=SURFACE)
            col.pack(side="left", expand=True)
            em = MOOD_LABELS.get(d['mood'], "😐").split()[0]
            tk.Label(col, text=em, bg=SURFACE, font=("Segoe UI",10)).pack()
            tk.Label(col, text=d['entry_date'][-5:], bg=SURFACE,
                     fg=TEXT_DIM, font=("Consolas",6)).pack()

    def _build_top_bottom(self):
        monthly = db.get_monthly_stats(date.today().year, date.today().month)
        if not monthly: return
        section = self._section("ТОП ТА АУТСАЙДЕРИ МІСЯЦЯ", STREAK)

        cols = tk.Frame(section, bg=SURFACE, padx=16, pady=8)
        cols.pack(fill="x")

        left = tk.Frame(cols, bg=SURFACE)
        left.pack(side="left", fill="both", expand=True, padx=(0,16))
        tk.Label(left, text="🏆 Найкращі", bg=SURFACE, fg=DONE,
                 font=FONT_BOLD).pack(anchor="w", pady=(0,6))
        for h in sorted([h for h in monthly if h['logged']>=3], key=lambda x: -x['pct'])[:5]:
            row = tk.Frame(left, bg=SURFACE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{h['emoji']} {h['name']}", bg=SURFACE,
                     fg=TEXT, font=FONT_MONO, width=22, anchor="w").pack(side="left")
            clr = DONE if h['pct']>=70 else STREAK
            tk.Label(row, text=f"{h['pct']}%", bg=SURFACE, fg=clr,
                     font=("Consolas",9,"bold")).pack(side="left")

        right = tk.Frame(cols, bg=SURFACE)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="⚠️ Потребують уваги", bg=SURFACE, fg=FAIL,
                 font=FONT_BOLD).pack(anchor="w", pady=(0,6))
        for h in sorted([h for h in monthly if h['logged']>=3], key=lambda x: x['pct'])[:5]:
            row = tk.Frame(right, bg=SURFACE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{h['emoji']} {h['name']}", bg=SURFACE,
                     fg=TEXT, font=FONT_MONO, width=22, anchor="w").pack(side="left")
            tk.Label(row, text=f"{h['pct']}%", bg=SURFACE, fg=FAIL,
                     font=("Consolas",9,"bold")).pack(side="left")

    def _embed_fig(self, fig, title, color):
        section = self._section(title, color)
        canvas = self._FCA(fig, master=section)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=16, pady=(0,8))
        self._plt.close(fig)
