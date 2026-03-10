"""
SelfMaster - Reusable Widgets
"""
import tkinter as tk
from tkinter import ttk
from .theme import *


def card_frame(parent, **kwargs):
    """Dark surface card frame."""
    f = tk.Frame(parent, bg=SURFACE, **kwargs)
    return f


def section_title(parent, text, color=TEXT_DIM):
    lbl = tk.Label(parent, text=text.upper(), bg=SURFACE,
                   fg=color, font=("Consolas", 9), anchor="w")
    return lbl


def stat_card(parent, label, value_var, sub="", color=ACCENT, width=140):
    """Mini stat card widget."""
    f = tk.Frame(parent, bg=SURFACE, width=width, padx=14, pady=12)
    f.pack_propagate(False)

    top_line = tk.Frame(f, bg=color, height=2)
    top_line.pack(fill="x")

    tk.Label(f, text=label.upper(), bg=SURFACE, fg=TEXT_DIM,
             font=("Consolas", 8), anchor="w").pack(fill="x", pady=(6, 2))

    val_lbl = tk.Label(f, textvariable=value_var if isinstance(value_var, tk.StringVar) else None,
                       text=value_var if isinstance(value_var, str) else "",
                       bg=SURFACE, fg=color, font=("Segoe UI", 22, "bold"), anchor="w")
    val_lbl.pack(fill="x")

    if sub:
        tk.Label(f, text=sub, bg=SURFACE, fg=TEXT_DIM,
                 font=("Consolas", 8), anchor="w").pack(fill="x")

    return f, val_lbl


def scrollable_frame(parent, bg=None):
    """Returns (outer_frame, inner_frame) with scrollbar."""
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

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return outer, inner


def hscrollable_frame(parent, bg=None):
    """Returns (outer_frame, inner_frame) with horizontal scrollbar."""
    bg = bg or BG
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    sb = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
    vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(xscrollcommand=sb.set, yscrollcommand=vsb.set)

    vsb.pack(side="right", fill="y")
    sb.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return outer, inner


class RoundedButton(tk.Canvas):
    """Canvas-based rounded button."""
    def __init__(self, parent, text, command=None, color=ACCENT,
                 fg=BG, width=120, height=36, radius=8, font=FONT_BOLD, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self._color = color
        self._fg = fg
        self._text = text
        self._command = command
        self._r = radius
        self._w = width
        self._h = height
        self._font = font
        self._draw()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, color=None):
        self.delete("all")
        c = color or self._color
        r = self._r
        w, h = self._w, self._h
        self.create_polygon(
            r, 0, w-r, 0, w, r, w, h-r, w-r, h, r, h, 0, h-r, 0, r,
            fill=c, outline="", smooth=True
        )
        self.create_text(w//2, h//2, text=self._text, fill=self._fg,
                         font=self._font)

    def _on_click(self, e):
        if self._command:
            self._command()

    def _on_enter(self, e):
        # slightly lighter
        self._draw(self._color + "cc")

    def _on_leave(self, e):
        self._draw()


class ProgressRing(tk.Canvas):
    """Circular progress indicator."""
    def __init__(self, parent, value=0, max_val=100, size=80,
                 color=ACCENT, bg=SURFACE, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=bg, highlightthickness=0, **kwargs)
        self._size = size
        self._color = color
        self._bg = bg
        self.set(value, max_val)

    def set(self, value, max_val=100):
        self.delete("all")
        s = self._size
        pad = 6
        extent = (value / max_val * 360) if max_val > 0 else 0

        # Background arc
        self.create_arc(pad, pad, s-pad, s-pad,
                        start=90, extent=360,
                        outline=BORDER, width=6, style="arc")
        # Value arc
        if extent > 0:
            self.create_arc(pad, pad, s-pad, s-pad,
                            start=90, extent=-extent,
                            outline=self._color, width=6, style="arc")

        # Text
        pct = f"{int(value/max_val*100)}%" if max_val > 0 else "—"
        self.create_text(s//2, s//2, text=pct,
                         fill=TEXT, font=("Segoe UI", int(s*0.18), "bold"))


class MoodPicker(tk.Frame):
    """5-star mood selector."""
    def __init__(self, parent, label="", initial=3, callback=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._val = tk.IntVar(value=initial)
        self._cb = callback
        self._btns = []

        if label:
            tk.Label(self, text=label, bg=BG, fg=TEXT_DIM,
                     font=FONT_MONO).pack(side="left", padx=(0, 8))

        for i in range(1, 6):
            emoji = MOOD_LABELS[i].split()[0]
            btn = tk.Label(self, text=emoji, bg=BG,
                           font=("Segoe UI", 16), cursor="hand2")
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, v=i: self._select(v))
            self._btns.append(btn)

        self._refresh()

    def _select(self, val):
        self._val.set(val)
        self._refresh()
        if self._cb:
            self._cb(val)

    def _refresh(self):
        v = self._val.get()
        for i, btn in enumerate(self._btns, 1):
            btn.configure(fg=MOOD_COLORS.get(i, TEXT_DIM) if i <= v else TEXT_DIM)

    def get(self):
        return self._val.get()

    def set(self, val):
        self._val.set(val)
        self._refresh()


class ScoreSlider(tk.Frame):
    """0-5 score selector with dot buttons."""
    def __init__(self, parent, initial=0, callback=None, **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)
        self._val = initial
        self._cb = callback
        self._btns = []

        for i in range(6):
            btn = tk.Label(self, text="●" if i == 0 else str(i),
                           bg=SURFACE, font=("Segoe UI", 11), cursor="hand2",
                           width=2)
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, v=i: self._select(v))
            self._btns.append(btn)

        self._refresh()

    def _select(self, val):
        self._val = val
        self._refresh()
        if self._cb:
            self._cb(val)

    def _refresh(self):
        for i, btn in enumerate(self._btns):
            if i == 0:
                btn.configure(fg=TEXT_DIM if self._val > 0 else FAIL)
                continue
            if i <= self._val:
                colors = [None, FAIL, STREAK, ACCENT3, ACCENT, SUCCESS]
                btn.configure(fg=colors[self._val] if self._val < len(colors) else ACCENT)
            else:
                btn.configure(fg=BORDER)

    def get(self):
        return self._val

    def set(self, val):
        self._val = val
        self._refresh()


class TagBadge(tk.Label):
    """Small colored tag/badge."""
    def __init__(self, parent, text, color=ACCENT3, **kwargs):
        super().__init__(parent, text=f" {text} ",
                         bg=color + "22", fg=color,
                         font=("Consolas", 8),
                         relief="flat", **kwargs)


def separator(parent, color=BORDER, orient="horizontal", pady=8):
    if orient == "horizontal":
        f = tk.Frame(parent, bg=color, height=1)
        f.pack(fill="x", pady=pady)
    else:
        f = tk.Frame(parent, bg=color, width=1)
        f.pack(fill="y", padx=pady, side="left")
    return f


def labeled_entry(parent, label, var=None, placeholder="", width=30, bg=None):
    """Label + Entry pair."""
    bg = bg or BG
    f = tk.Frame(parent, bg=bg)
    tk.Label(f, text=label, bg=bg, fg=TEXT_DIM, font=FONT_MONO).pack(anchor="w")
    if var is None:
        var = tk.StringVar()
    e = tk.Entry(f, textvariable=var, bg=SURFACE2, fg=TEXT,
                 font=FONT_MAIN, relief="flat", insertbackground=TEXT,
                 width=width, bd=0,
                 highlightthickness=1, highlightcolor=ACCENT3,
                 highlightbackground=BORDER)
    e.pack(fill="x", ipady=6, pady=(2, 0))
    return f, var
