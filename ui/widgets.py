"""SelfMaster — Reusable Widgets"""
import tkinter as tk
from tkinter import ttk
from ui.theme import *


def scrollable_frame(parent, bg=None):
    bg = bg or BG
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    def _scroll(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _scroll)
    return outer, inner


def hscrollable_frame(parent, bg=None):
    bg = bg or BG
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    hsb = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
    vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    def _scroll(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _scroll)
    return outer, inner


def card(parent, accent_color=None, padx=16, pady=12, **kwargs):
    f = tk.Frame(parent, bg=SURFACE, padx=padx, pady=pady, **kwargs)
    if accent_color:
        tk.Frame(f, bg=accent_color, height=2).pack(fill="x")
    return f


def section_header(parent, title, color=TEXT_DIM):
    hdr = tk.Frame(parent, bg=BG)
    hdr.pack(fill="x", pady=(12, 4))
    tk.Label(hdr, text=title, bg=BG, fg=color,
             font=("Consolas", 8, "bold")).pack(side="left")
    tk.Frame(hdr, bg=BORDER, height=1).pack(
        side="left", fill="x", expand=True, padx=(8, 0), pady=10)
    return hdr


def labeled_entry(parent, label, var=None, width=30, bg=None, **kwargs):
    bg = bg or SURFACE2
    f = tk.Frame(parent, bg=bg)
    tk.Label(f, text=label, bg=bg, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
    if var is None:
        var = tk.StringVar()
    e = tk.Entry(f, textvariable=var, bg=SURFACE3, fg=TEXT,
                 font=FONT_MAIN, relief="flat", insertbackground=TEXT,
                 width=width, bd=0,
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BORDER, **kwargs)
    e.pack(fill="x", ipady=7, pady=(3, 0))
    return f, var


def pill_badge(parent, text, color=ACCENT, **kwargs):
    return tk.Label(parent, text=f" {text} ",
                    bg=_hex_fade(color, 0.15), fg=color,
                    font=("Consolas", 8), relief="flat", **kwargs)

def _hex_fade(hex_color, alpha):
    """Simulate transparent color by blending with SURFACE."""
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        sr = int(SURFACE[1:3], 16)
        sg = int(SURFACE[3:5], 16)
        sb = int(SURFACE[5:7], 16)
        nr = int(r*alpha + sr*(1-alpha))
        ng = int(g*alpha + sg*(1-alpha))
        nb = int(b*alpha + sb*(1-alpha))
        return f"#{nr:02x}{ng:02x}{nb:02x}"
    except: return SURFACE2


class MoodPicker(tk.Frame):
    def __init__(self, parent, initial=3, callback=None, **kwargs):
        super().__init__(parent, bg=kwargs.pop('bg', SURFACE), **kwargs)
        self._val = tk.IntVar(value=initial)
        self._cb = callback
        self._btns = []
        for i in range(1, 6):
            em = MOOD_LABELS[i].split()[0]
            btn = tk.Label(self, text=em, bg=self['bg'],
                           font=("Segoe UI", 15), cursor="hand2")
            btn.pack(side="left", padx=3)
            btn.bind("<Button-1>", lambda e, v=i: self._select(v))
            self._btns.append(btn)
        self._refresh()

    def _select(self, val):
        self._val.set(val)
        self._refresh()
        if self._cb: self._cb(val)

    def _refresh(self):
        v = self._val.get()
        for i, btn in enumerate(self._btns, 1):
            btn.configure(fg=MOOD_COLORS.get(i, TEXT_DIM) if i <= v else BORDER)

    def get(self): return self._val.get()
    def set(self, val): self._val.set(val); self._refresh()


class ScoreSlider(tk.Frame):
    def __init__(self, parent, initial=0, callback=None, **kwargs):
        bg = kwargs.pop('bg', SURFACE)
        super().__init__(parent, bg=bg, **kwargs)
        self._val = initial
        self._cb = callback
        self._bg = bg
        self._btns = []
        score_colors = ["", FAIL, STREAK, ACCENT3, ACCENT, SUCCESS]
        for i in range(6):
            txt = "●" if i == 0 else str(i)
            btn = tk.Label(self, text=txt, bg=bg,
                           font=("Segoe UI", 12), cursor="hand2", width=2)
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, v=i: self._select(v))
            self._btns.append(btn)
        self._refresh()

    def _select(self, val):
        self._val = val
        self._refresh()
        if self._cb: self._cb(val)

    def _refresh(self):
        score_colors = ["", FAIL, STREAK, ACCENT3, ACCENT, SUCCESS]
        for i, btn in enumerate(self._btns):
            if i == 0:
                btn.configure(fg=TEXT_DIM if self._val > 0 else BORDER)
            elif i <= self._val:
                btn.configure(fg=score_colors[self._val] if self._val < len(score_colors) else ACCENT)
            else:
                btn.configure(fg=BORDER)

    def get(self): return self._val
    def set(self, val): self._val = val; self._refresh()


class GlowButton(tk.Canvas):
    """Animated glow button."""
    def __init__(self, parent, text, command=None, color=ACCENT,
                 fg=TEXT, width=130, height=38, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent['bg'] if 'bg' not in kwargs else kwargs.pop('bg'),
                         highlightthickness=0, **kwargs)
        self._color = color
        self._fg = fg
        self._text = text
        self._cmd = command
        self._w = width
        self._h = height
        self._hover = False
        self._draw()
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)

    def _draw(self, hover=False):
        self.delete("all")
        c = self._color
        r = 8
        w, h = self._w, self._h
        bg = _hex_fade(c, 0.25 if hover else 0.15)
        pts = [r,0, w-r,0, w,r, w,h-r, w-r,h, r,h, 0,h-r, 0,r]
        self.create_polygon(pts, fill=bg, outline=c if hover else BORDER, width=1, smooth=True)
        self.create_text(w//2, h//2, text=self._text, fill=self._fg if hover else TEXT_MID,
                         font=FONT_BOLD)

    def _click(self, e):
        if self._cmd: self._cmd()

    def _enter(self, e): self._draw(True)
    def _leave(self, e): self._draw(False)


class ProgressBar(tk.Frame):
    def __init__(self, parent, value=0, max_val=100, color=ACCENT,
                 height=6, show_text=False, **kwargs):
        bg = kwargs.pop('bg', SURFACE)
        super().__init__(parent, bg=bg, **kwargs)
        self._color = color
        self._height = height
        self._show_text = show_text
        self._bar_bg = tk.Frame(self, bg=SURFACE3, height=height)
        self._bar_bg.pack(fill="x")
        self._bar_fill = tk.Frame(self._bar_bg, bg=color, height=height)
        self._bar_fill.place(x=0, y=0, relheight=1)
        self.set(value, max_val)

    def set(self, value, max_val=100):
        pct = max(0, min(1, value/max_val)) if max_val else 0
        self._bar_fill.place(relwidth=pct, relheight=1)
