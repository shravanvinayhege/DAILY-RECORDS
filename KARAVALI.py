import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import numpy as np

import sys, os

def resource_path(relative_path):
    """For bundled READ-ONLY assets (icon, images, etc.)"""
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def db_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "karavali_records.db")


# ══════════════════════════════════════════════════════════════════════════════
#  PALETTE
# ══════════════════════════════════════════════════════════════════════════════
BG          = "#0A0A0A"
BG2         = "#111111"
SURFACE     = "#161616"
SURFACE2    = "#1C1C1C"
SURFACE3    = "#242424"
BORDER      = "#2A2A2A"
BORDER2     = "#3A3A3A"
MUTED       = "#3D3D3D"
TEXT        = "#FFFFFF"
TEXT2       = "#F0F0F0"
TEXT3       = "#E0E0E0"
TEXT4       = "#B8B8B8"
ACCENT      = "#D4D4D4"
ACCENT_DIM  = "#C0C0C0"
FACTORY_AC  = "#C0C0C0"
FACTORY_DIM = "#909090"
SUCCESS     = "#6EE7B7"
SUCCESS_BG  = "#071A12"
DANGER      = "#FCA5A5"
DANGER_BG   = "#1A0707"
WARNING     = "#FCD34D"
INFO        = "#93C5FD"
HIGHLIGHT   = "#C4B5FD"
ENTRY_BG    = "#0E0E0E"
SUBFIELD_BG = "#0D0D18"
HEADER_BG   = "#141414"
CH_SALES    = "#A8D8A8"
CH_PROFIT   = "#87CEEB"
CH_EXPENSE  = "#E8A0A0"
CH_PURCHASE = "#C8A8D8"
CH_SALARY   = "#FAD7A0"
CH_CLOSING  = "#B0C4DE"
CH_VEHICLE  = "#B8D8B8"

FONT_BRAND  = ("Courier New", 9)
FONT_LABEL  = ("Segoe UI", 9)
FONT_ENTRY  = ("Consolas", 11)
FONT_BTN    = ("Segoe UI Semibold", 9)
FONT_HEAD   = ("Courier New", 13, "bold")
FONT_SECTION= ("Courier New", 8, "bold")
FONT_NET    = ("Consolas", 22, "bold")
FONT_STAT   = ("Consolas", 10, "bold")
FONT_SMALL  = ("Segoe UI", 8)
FONT_SUBLBL = ("Segoe UI", 8)
FONT_SUBENT = ("Consolas", 10)

APP_PASSWORD = "12345"


conn = sqlite3.connect(db_path())
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS parlor_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE,
    opening_balance REAL DEFAULT 0,
    misc_expenses REAL DEFAULT 0,
    ice_cream_purchases REAL DEFAULT 0,
    keb_honnaver REAL DEFAULT 0,
    keb_ramthirth REAL DEFAULT 0,
    pigmy REAL DEFAULT 0,
    milk_expenses REAL DEFAULT 0,
    day_sales REAL DEFAULT 0
)""")


c.execute("""CREATE TABLE IF NOT EXISTS factory_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE,
    opening_balance REAL DEFAULT 0,
    misc_expenses REAL DEFAULT 0,
    ice_cream_purchases REAL DEFAULT 0,
    keb_honnaver REAL DEFAULT 0,
    keb_ramthirth REAL DEFAULT 0,
    pigmy REAL DEFAULT 0,
    milk_expenses REAL DEFAULT 0,
    day_sales REAL DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS salary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    record_type TEXT,
    employee_name TEXT,
    amount REAL DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS vehicle_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    record_type TEXT,
    vehicle_number TEXT,
    petrol REAL DEFAULT 0,
    maintenance REAL DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS misc_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    record_type TEXT,
    purpose TEXT,
    amount REAL DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS keb_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    record_type TEXT,
    meter_name TEXT,
    amount REAL DEFAULT 0
)""")

def _add_col_if_missing(table, col, col_def):
    c.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in c.fetchall()]
    if col not in cols:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")

for tbl in ("parlor_records", "factory_records"):
    _add_col_if_missing(tbl, "keb_honnaver",        "REAL DEFAULT 0")
    _add_col_if_missing(tbl, "keb_ramthirth",       "REAL DEFAULT 0")
    _add_col_if_missing(tbl, "milk_expenses",       "REAL DEFAULT 0")
    _add_col_if_missing(tbl, "day_sales",           "REAL DEFAULT 0")
    _add_col_if_missing(tbl, "ice_cream_purchases", "REAL DEFAULT 0")
    _add_col_if_missing(tbl, "pigmy",               "REAL DEFAULT 0")

conn.commit()


def make_button(parent, text, cmd, color=SURFACE2, hover=SURFACE3,
                fg=TEXT2, width=None, pady=9, padx=16):
    kw = dict(text=text, command=cmd, bg=color, fg=fg,
              activebackground=hover, activeforeground=fg,
              font=FONT_BTN, relief="flat", bd=0,
              cursor="hand2", padx=padx, pady=pady)
    if width: kw["width"] = width
    btn = tk.Button(parent, **kw)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def styled_entry(parent, ph="", bg_override=None):
    ebg = bg_override if bg_override else ENTRY_BG
    outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
    ent = tk.Entry(outer, bg=ebg, fg=TEXT,
                   insertbackground=TEXT2, relief="flat",
                   font=FONT_ENTRY, bd=0, highlightthickness=0)
    ent.pack(fill="x", ipady=8, padx=7)
    if ph:
        ent.insert(0, ph); ent.config(fg=TEXT3)
        def fi(e):
            if ent.get() == ph: ent.delete(0, tk.END); ent.config(fg=TEXT)
            outer.config(bg=BORDER2)
        def fo(e):
            if ent.get() == "": ent.insert(0, ph); ent.config(fg=TEXT3)
            outer.config(bg=BORDER)
        ent.bind("<FocusIn>", fi); ent.bind("<FocusOut>", fo)
    return outer, ent

def form_row(parent, label, ph="0.00", icon="\u2014", bg=SURFACE):
    row = tk.Frame(parent, bg=bg); row.pack(fill="x", pady=3)
    lf = tk.Frame(row, bg=bg); lf.pack(fill="x")
    tk.Label(lf, text=icon, bg=bg, fg=TEXT4, font=("Consolas", 9)).pack(side="left")
    tk.Label(lf, text="  " + label, bg=bg, fg=TEXT3, font=FONT_LABEL, anchor="w").pack(side="left")
    frm, ent = styled_entry(row, ph)
    frm.pack(fill="x", pady=(2, 0))
    return row, ent

def section_hdr(parent, text, bg=SURFACE):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=(12, 0))
    f = tk.Frame(parent, bg=bg); f.pack(fill="x", pady=(5, 6))
    tk.Label(f, text=text, bg=bg, fg=TEXT3, font=FONT_SECTION).pack(side="left", padx=2)

def scrollable_frame(parent, bg=SURFACE):
    canvas = tk.Canvas(parent, bg=bg, highlightthickness=0, bd=0)
    sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=bg)
    cw = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    return inner

def get_float(ent, ph="0.00"):
    v = ent.get().strip()
    if v == ph or v == "": return 0.0
    try: return float(v)
    except: return 0.0

def apply_chart_style(ax, fig):
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#161616")
    ax.tick_params(colors=TEXT3, labelsize=8)
    for spine in ax.spines.values(): spine.set_edgecolor(BORDER)
    ax.grid(True, color=BORDER, linewidth=0.4, alpha=0.7, linestyle="--")
    ax.set_axisbelow(True)
    ax.title.set_color(TEXT2); ax.title.set_fontsize(9)

def date_exists(date_val, mode, exclude_id=None):
    tbl = "factory_records" if mode == "factory" else "parlor_records"
    if exclude_id:
        c.execute(f"SELECT id FROM {tbl} WHERE date=? AND id!=?", (date_val, exclude_id))
    else:
        c.execute(f"SELECT id FROM {tbl} WHERE date=?", (date_val,))
    return c.fetchone() is not None


def show_password_screen(root, on_success):
    """Show full-window password overlay. Calls on_success() when correct."""
    overlay = tk.Frame(root, bg=BG)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    overlay.lift()

    card_outer = tk.Frame(overlay, bg=BG)
    card_outer.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(card_outer, text="KARAVALI", bg=BG, fg=TEXT,
             font=("Courier New", 28, "bold")).pack(pady=(0, 4))
    tk.Label(card_outer, text="ICE CREAM  \u00b7  FINANCIAL MANAGEMENT",
             bg=BG, fg=TEXT4, font=FONT_BRAND).pack()
    tk.Frame(card_outer, bg=ACCENT, height=2, width=340).pack(pady=(18, 0))

    card = tk.Frame(card_outer, bg=SURFACE, padx=40, pady=36)
    card.pack(fill="x", pady=0)
    tk.Frame(card_outer, bg=ACCENT, height=2, width=340).pack()

    tk.Label(card, text="\U0001f512  ENTER PASSWORD", bg=SURFACE, fg=TEXT3,
             font=FONT_SECTION).pack(anchor="w", pady=(0, 14))

    pw_frame = tk.Frame(card, bg=BORDER, padx=1, pady=1)
    pw_frame.pack(fill="x")
    pw_entry = tk.Entry(pw_frame, bg=ENTRY_BG, fg=TEXT, show="\u2022",
                        insertbackground=TEXT2, relief="flat",
                        font=("Consolas", 14), bd=0, highlightthickness=0)
    pw_entry.pack(fill="x", ipady=10, padx=10)

    err_var = tk.StringVar()
    err_lbl = tk.Label(card, textvariable=err_var, bg=SURFACE, fg=DANGER,
                       font=("Consolas", 9))
    err_lbl.pack(pady=(8, 0))

    attempts = [0]

    def check_password(event=None):
        entered = pw_entry.get()
        if entered == APP_PASSWORD:
            overlay.destroy()
            on_success()
        else:
            attempts[0] += 1
            pw_entry.delete(0, tk.END)
            err_var.set(f"\u2715  Incorrect password. Attempt {attempts[0]}.")
            pw_frame.config(bg=DANGER)
            card_outer.after(600, lambda: pw_frame.config(bg=BORDER))

    pw_entry.bind("<Return>", check_password)

    btn = make_button(card, "  Unlock  ", check_password,
                      color=SURFACE3, hover=MUTED, fg=ACCENT, padx=24, pady=11)
    btn.pack(fill="x", pady=(16, 0))

    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        pw_entry.config(show="" if show_var.get() else "\u2022")
    chk = tk.Checkbutton(card, text="Show password", variable=show_var,
                         command=toggle_show, bg=SURFACE, fg=TEXT4,
                         selectcolor=SURFACE3, activebackground=SURFACE,
                         font=FONT_SMALL, bd=0, cursor="hand2")
    chk.pack(anchor="w", pady=(10, 0))

    tk.Label(card_outer, text=f"\u00a9 {datetime.now().year} Karavali Ice Cream",
             bg=BG, fg=MUTED, font=FONT_SMALL).pack(pady=(18, 0))

    pw_entry.focus_set()


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class SalaryWidget:
    def __init__(self, parent, bg=SURFACE, on_change=None):
        self.bg = bg; self.on_change = on_change; self.rows = []
        self.outer = tk.Frame(parent, bg=bg); self.outer.pack(fill="x", pady=(0, 4))
        hdr = tk.Frame(self.outer, bg=bg); hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="\u2014  Salary & Allowances", bg=bg, fg=TEXT3, font=FONT_LABEL).pack(side="left")
        make_button(hdr, "+ Add Employee", self.add_row, color=SURFACE3, hover=MUTED, fg=HIGHLIGHT, padx=8, pady=3).pack(side="right")
        self.rows_frame = tk.Frame(self.outer, bg=bg); self.rows_frame.pack(fill="x")
        self.total_var = tk.StringVar(value="Total: Rs 0.00")
        tk.Label(self.outer, textvariable=self.total_var, bg=bg, fg=TEXT3, font=FONT_SMALL).pack(anchor="e", pady=(2, 0))
        self.add_row()

    def add_row(self, default_name="", default_amt=""):
        row_bg = SURFACE2 if len(self.rows) % 2 == 0 else SURFACE
        rf = tk.Frame(self.rows_frame, bg=BORDER, pady=1, padx=1); rf.pack(fill="x", pady=2)
        inner = tk.Frame(rf, bg=row_bg); inner.pack(fill="x")
        name_ph = "Employee name"
        name_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT2, insertbackground=HIGHLIGHT,
                            relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0)
        if default_name:
            name_ent.insert(0, default_name); name_ent.config(fg=TEXT2)
        else:
            name_ent.insert(0, name_ph); name_ent.config(fg=TEXT3)
        name_ent.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 4))
        def nfi(e):
            if name_ent.get() == name_ph: name_ent.delete(0, tk.END); name_ent.config(fg=TEXT2)
        def nfo(e):
            if name_ent.get() == "": name_ent.insert(0, name_ph); name_ent.config(fg=TEXT3)
        name_ent.bind("<FocusIn>", nfi); name_ent.bind("<FocusOut>", nfo)
        amt_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT2, insertbackground=HIGHLIGHT,
                           relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0, width=10)
        if default_amt:
            amt_ent.insert(0, default_amt); amt_ent.config(fg=TEXT2)
        else:
            amt_ent.insert(0, "0.00"); amt_ent.config(fg=TEXT3)
        amt_ent.pack(side="left", ipady=6, padx=(0, 4))
        def afi(e):
            if amt_ent.get() == "0.00": amt_ent.delete(0, tk.END); amt_ent.config(fg=TEXT2)
        def afo(e):
            if amt_ent.get() == "": amt_ent.insert(0, "0.00"); amt_ent.config(fg=TEXT3)
            self._update_total()
            if self.on_change: self.on_change()
        amt_ent.bind("<FocusIn>", afi); amt_ent.bind("<FocusOut>", afo)
        amt_ent.bind("<KeyRelease>", lambda e: (self._update_total(), self.on_change() if self.on_change else None))
        def remove(rf=rf):
            for i, (n, a, r) in enumerate(self.rows):
                if r is rf:
                    self.rows.pop(i); rf.destroy(); self._update_total()
                    if self.on_change: self.on_change()
                    break
        if len(self.rows) > 0:
            tk.Button(inner, text="\u00d7", bg=row_bg, fg=DANGER, relief="flat", bd=0,
                      font=("Consolas", 12), cursor="hand2", padx=6, command=remove).pack(side="right", padx=(0, 4))
        self.rows.append((name_ent, amt_ent, rf)); self._update_total()

    def _update_total(self):
        total = 0.0
        for _, a, _ in self.rows:
            v = a.get().strip()
            if v not in ("", "0.00"):
                try: total += float(v)
                except: pass
        self.total_var.set(f"Total: Rs {total:,.2f}")

    def get_entries(self):
        result = []
        for n, a, r in self.rows:
            name = n.get().strip()
            if name == "Employee name": name = ""
            amt = 0.0
            try:
                v = a.get().strip()
                if v not in ("", "0.00"): amt = float(v)
            except: pass
            if name or amt > 0: result.append((name, amt))
        return result

    def get_total(self): return sum(amt for _, amt in self.get_entries())

    def reset(self):
        for n, a, r in self.rows: r.destroy()
        self.rows.clear(); self.add_row(); self._update_total()

    def load(self, entries):
        for n, a, r in self.rows: r.destroy()
        self.rows.clear()
        for name, amt in entries:
            self.add_row(default_name=name, default_amt=str(amt))
        if not entries: self.add_row()
        self._update_total()


class VehicleWidget:
    def __init__(self, parent, bg=SURFACE, on_change=None):
        self.bg = bg; self.on_change = on_change; self.rows = []
        self.outer = tk.Frame(parent, bg=bg); self.outer.pack(fill="x", pady=(0, 4))
        hdr = tk.Frame(self.outer, bg=bg); hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="\u2014  Vehicle Petrol & Maintenance", bg=bg, fg=TEXT3, font=FONT_LABEL).pack(side="left")
        make_button(hdr, "+ Add Vehicle", self.add_row, color=SURFACE3, hover=MUTED, fg=INFO, padx=8, pady=3).pack(side="right")
        col_hdr = tk.Frame(self.outer, bg=bg); col_hdr.pack(fill="x", pady=(0, 2))
        tk.Label(col_hdr, text="  Vehicle ", bg=bg, fg=TEXT4, font=FONT_SMALL, width=16, anchor="w").pack(side="left")
        tk.Label(col_hdr, text="Petrol (Rs)", bg=bg, fg=TEXT4, font=FONT_SMALL, width=12, anchor="w").pack(side="left", padx=(4,0))
        tk.Label(col_hdr, text="Maint (Rs)", bg=bg, fg=TEXT4, font=FONT_SMALL, width=12, anchor="w").pack(side="left", padx=(4,0))
        self.rows_frame = tk.Frame(self.outer, bg=bg); self.rows_frame.pack(fill="x")
        self.total_var = tk.StringVar(value="Total: Rs 0.00")
        tk.Label(self.outer, textvariable=self.total_var, bg=bg, fg=TEXT3, font=FONT_SMALL).pack(anchor="e", pady=(2, 0))
        self.add_row()

    def add_row(self, default_veh="KA", default_pet="", default_maint=""):
        row_bg = SURFACE2 if len(self.rows) % 2 == 0 else SURFACE
        rf = tk.Frame(self.rows_frame, bg=BORDER, pady=1, padx=1); rf.pack(fill="x", pady=2)
        inner = tk.Frame(rf, bg=row_bg); inner.pack(fill="x")

        veh_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT2, insertbackground=INFO,
                           relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0, width=12)
        veh_ent.insert(0, default_veh if default_veh else "KA")
        veh_ent.config(fg=TEXT2)
        veh_ent.pack(side="left", ipady=5, padx=(6, 4))

        def _enforce_ka(event):
            v = veh_ent.get()
            if not v.upper().startswith("KA"):
                veh_ent.delete(0, tk.END)
                veh_ent.insert(0, "KA")
        veh_ent.bind("<FocusOut>", _enforce_ka)
        veh_ent.bind("<KeyRelease>", lambda e: (setattr(e, '_dummy', None), _check_ka(veh_ent)))

        def _check_ka(w):
            v = w.get()
            if len(v) >= 2 and not v.upper().startswith("KA"):
                w.delete(0, tk.END); w.insert(0, "KA")

        def make_num_entry(default=""):
            ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT3, insertbackground=HIGHLIGHT,
                           relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0, width=10)
            val = default if default else "0.00"
            ent.insert(0, val); ent.config(fg=TEXT2 if default else TEXT3)
            def fi(e):
                if ent.get() == "0.00": ent.delete(0, tk.END); ent.config(fg=TEXT2)
            def fo(e):
                if ent.get() == "": ent.insert(0, "0.00"); ent.config(fg=TEXT3)
                self._update_total()
                if self.on_change: self.on_change()
            ent.bind("<FocusIn>", fi); ent.bind("<FocusOut>", fo)
            ent.bind("<KeyRelease>", lambda e: (self._update_total(), self.on_change() if self.on_change else None))
            ent.pack(side="left", ipady=5, padx=(0, 4))
            return ent

        petrol_ent = make_num_entry(default_pet)
        maint_ent  = make_num_entry(default_maint)

        def remove(rf=rf):
            for i, (v, p, m, r) in enumerate(self.rows):
                if r is rf:
                    self.rows.pop(i); rf.destroy(); self._update_total()
                    if self.on_change: self.on_change()
                    break
        if len(self.rows) > 0:
            tk.Button(inner, text="\u00d7", bg=row_bg, fg=DANGER, relief="flat", bd=0,
                      font=("Consolas", 12), cursor="hand2", padx=6, command=remove).pack(side="right", padx=(0, 4))
        self.rows.append((veh_ent, petrol_ent, maint_ent, rf)); self._update_total()

    def _update_total(self):
        total = 0.0
        for v, p, m, r in self.rows:
            for ent in (p, m):
                val = ent.get().strip()
                if val not in ("", "0.00"):
                    try: total += float(val)
                    except: pass
        self.total_var.set(f"Total: Rs {total:,.2f}")

    def get_entries(self):
        result = []
        for v, p, m, r in self.rows:
            vno = v.get().strip().upper()
            if not vno.startswith("KA"): vno = "KA" + vno
            pet = 0.0; maint = 0.0
            try:
                if p.get().strip() not in ("", "0.00"): pet = float(p.get())
            except: pass
            try:
                if m.get().strip() not in ("", "0.00"): maint = float(m.get())
            except: pass
            if pet > 0 or maint > 0: result.append((vno, pet, maint))
        return result

    def get_total_petrol(self): return sum(p for _, p, _ in self.get_entries())
    def get_total_maint(self):  return sum(m for _, _, m in self.get_entries())

    def reset(self):
        for v, p, m, r in self.rows: r.destroy()
        self.rows.clear(); self.add_row(); self._update_total()

    def load(self, entries):
        for v, p, m, r in self.rows: r.destroy()
        self.rows.clear()
        for vno, pet, maint in entries:
            self.add_row(default_veh=vno,
                         default_pet=str(pet) if pet else "",
                         default_maint=str(maint) if maint else "")
        if not entries: self.add_row()
        self._update_total()


class KEBWidget:
    """
    Fully customisable KEB electricity meter widget.
    No hardcoded meter names — user types any board/meter name they like.
    Start with one blank row; use '+ Add Meter' to add more.
    """
    def __init__(self, parent, bg=SURFACE, on_change=None):
        self.bg = bg; self.on_change = on_change; self.rows = []
        self.outer = tk.Frame(parent, bg=bg); self.outer.pack(fill="x", pady=(0, 4))

        hdr = tk.Frame(self.outer, bg=bg); hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="\u2014  KEB Electricity Meters", bg=bg, fg=TEXT3, font=FONT_LABEL).pack(side="left")
        make_button(hdr, "+ Add Meter", self.add_row, color=SURFACE3, hover=MUTED, fg=INFO, padx=8, pady=3).pack(side="right")

        col_hdr = tk.Frame(self.outer, bg=bg); col_hdr.pack(fill="x", pady=(0, 2))
        tk.Label(col_hdr, text="  Board / Meter Name", bg=bg, fg=TEXT4,
                 font=FONT_SMALL, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(col_hdr, text="Amount (Rs)", bg=bg, fg=TEXT4,
                 font=FONT_SMALL, width=14, anchor="w").pack(side="left", padx=(4, 0))

        self.rows_frame = tk.Frame(self.outer, bg=bg); self.rows_frame.pack(fill="x")

        self.total_var = tk.StringVar(value="Total: Rs 0.00")
        tk.Label(self.outer, textvariable=self.total_var, bg=bg, fg=TEXT3,
                 font=FONT_SMALL).pack(anchor="e", pady=(2, 0))

        # Start with one blank row — no preset names
        self.add_row()

    def add_row(self, default_name="", default_amt=""):
        row_bg = SURFACE2 if len(self.rows) % 2 == 0 else SURFACE
        rf = tk.Frame(self.rows_frame, bg=BORDER, pady=1, padx=1); rf.pack(fill="x", pady=2)
        inner = tk.Frame(rf, bg=row_bg); inner.pack(fill="x")

        # ── Meter / board name entry (fully free-text) ──
        name_ph = "Enter board / meter name"
        name_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT2, insertbackground=INFO,
                            relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0)
        if default_name:
            name_ent.insert(0, default_name); name_ent.config(fg=TEXT2)
        else:
            name_ent.insert(0, name_ph); name_ent.config(fg=TEXT3)
        name_ent.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 4))

        def nfi(e):
            if name_ent.get() == name_ph:
                name_ent.delete(0, tk.END); name_ent.config(fg=TEXT2)
        def nfo(e):
            if name_ent.get() == "":
                name_ent.insert(0, name_ph); name_ent.config(fg=TEXT3)
        name_ent.bind("<FocusIn>", nfi); name_ent.bind("<FocusOut>", nfo)

        # ── Amount entry ──
        amt_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT3, insertbackground=INFO,
                           relief="flat", font=("Consolas", 10), bd=0,
                           highlightthickness=0, width=11)
        if default_amt:
            amt_ent.insert(0, default_amt); amt_ent.config(fg=TEXT2)
        else:
            amt_ent.insert(0, "0.00")
        amt_ent.pack(side="left", ipady=6, padx=(0, 4))

        def afi(e):
            if amt_ent.get() == "0.00": amt_ent.delete(0, tk.END); amt_ent.config(fg=TEXT2)
        def afo(e):
            if amt_ent.get() == "": amt_ent.insert(0, "0.00"); amt_ent.config(fg=TEXT3)
            self._update_total()
            if self.on_change: self.on_change()
        amt_ent.bind("<FocusIn>", afi); amt_ent.bind("<FocusOut>", afo)
        amt_ent.bind("<KeyRelease>",
                     lambda e: (self._update_total(),
                                self.on_change() if self.on_change else None))

        # ── Remove button (always shown so user can delete any row) ──
        def remove(rf=rf):
            for i, (n, a, r) in enumerate(self.rows):
                if r is rf:
                    self.rows.pop(i); rf.destroy(); self._update_total()
                    if self.on_change: self.on_change()
                    break
        tk.Button(inner, text="\u00d7", bg=row_bg, fg=DANGER, relief="flat", bd=0,
                  font=("Consolas", 12), cursor="hand2", padx=6,
                  command=remove).pack(side="right", padx=(0, 4))

        self.rows.append((name_ent, amt_ent, rf))
        self._update_total()

    def _update_total(self):
        total = 0.0
        for n, a, r in self.rows:
            v = a.get().strip()
            if v not in ("", "0.00"):
                try: total += float(v)
                except: pass
        self.total_var.set(f"Total: Rs {total:,.2f}")

    def get_total(self):
        total = 0.0
        for n, a, r in self.rows:
            v = a.get().strip()
            if v not in ("", "0.00"):
                try: total += float(v)
                except: pass
        return total

    def get_all_values(self):
        """Returns {meter_name: amount} dict for all rows with valid entries."""
        result = {}
        name_ph = "Enter board / meter name"
        for n, a, r in self.rows:
            meter = n.get().strip()
            if meter == name_ph or meter == "": meter = "Unnamed Meter"
            amt = 0.0
            try:
                v = a.get().strip()
                if v not in ("", "0.00"): amt = float(v)
            except: pass
            if amt > 0:
                result[meter] = result.get(meter, 0) + amt
        return result

    def reset(self):
        for n, a, r in self.rows: r.destroy()
        self.rows.clear()
        self.add_row()          # single blank row on reset
        self._update_total()

    def load(self, keb_dict):
        """Load from a {meter_name: amount} dict (e.g. from saved records)."""
        for n, a, r in self.rows: r.destroy()
        self.rows.clear()
        for meter, amt in keb_dict.items():
            self.add_row(default_name=meter,
                         default_amt=str(amt) if amt else "")
        if not keb_dict:
            self.add_row()
        self._update_total()


class MiscWidget:
    def __init__(self, parent, bg=SURFACE, on_change=None):
        self.bg = bg; self.on_change = on_change; self.rows = []
        self.outer = tk.Frame(parent, bg=bg); self.outer.pack(fill="x", pady=(0, 4))
        hdr = tk.Frame(self.outer, bg=bg); hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="\u2014  Miscellaneous Expenses", bg=bg, fg=TEXT3, font=FONT_LABEL).pack(side="left")
        make_button(hdr, "+ Add Expense", self.add_row, color=SURFACE3, hover=MUTED, fg=WARNING, padx=8, pady=3).pack(side="right")
        col_hdr = tk.Frame(self.outer, bg=bg); col_hdr.pack(fill="x", pady=(0, 2))
        tk.Label(col_hdr, text="  Purpose / Description", bg=bg, fg=TEXT4, font=FONT_SMALL, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(col_hdr, text="Amount (Rs)", bg=bg, fg=TEXT4, font=FONT_SMALL, width=14, anchor="w").pack(side="left", padx=(4, 0))
        self.rows_frame = tk.Frame(self.outer, bg=bg); self.rows_frame.pack(fill="x")
        self.total_var = tk.StringVar(value="Total: Rs 0.00")
        tk.Label(self.outer, textvariable=self.total_var, bg=bg, fg=TEXT3, font=FONT_SMALL).pack(anchor="e", pady=(2, 0))
        self.add_row()

    def add_row(self, default_purpose="", default_amt=""):
        row_bg = SURFACE2 if len(self.rows) % 2 == 0 else SURFACE
        rf = tk.Frame(self.rows_frame, bg=BORDER, pady=1, padx=1); rf.pack(fill="x", pady=2)
        inner = tk.Frame(rf, bg=row_bg); inner.pack(fill="x")
        purpose_ph = "Purpose of expense"
        pur_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT3, insertbackground=WARNING,
                           relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0)
        if default_purpose:
            pur_ent.insert(0, default_purpose); pur_ent.config(fg=TEXT2)
        else:
            pur_ent.insert(0, purpose_ph)
        pur_ent.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 4))
        def pfi(e):
            if pur_ent.get() == purpose_ph: pur_ent.delete(0, tk.END); pur_ent.config(fg=TEXT2)
        def pfo(e):
            if pur_ent.get() == "": pur_ent.insert(0, purpose_ph); pur_ent.config(fg=TEXT3)
        pur_ent.bind("<FocusIn>", pfi); pur_ent.bind("<FocusOut>", pfo)
        amt_ent = tk.Entry(inner, bg=SUBFIELD_BG, fg=TEXT3, insertbackground=WARNING,
                           relief="flat", font=("Consolas", 10), bd=0, highlightthickness=0, width=11)
        if default_amt:
            amt_ent.insert(0, default_amt); amt_ent.config(fg=TEXT2)
        else:
            amt_ent.insert(0, "0.00")
        amt_ent.pack(side="left", ipady=6, padx=(0, 4))
        def afi(e):
            if amt_ent.get() == "0.00": amt_ent.delete(0, tk.END); amt_ent.config(fg=TEXT2)
        def afo(e):
            if amt_ent.get() == "": amt_ent.insert(0, "0.00"); amt_ent.config(fg=TEXT3)
            self._update_total()
            if self.on_change: self.on_change()
        amt_ent.bind("<FocusIn>", afi); amt_ent.bind("<FocusOut>", afo)
        amt_ent.bind("<KeyRelease>", lambda e: (self._update_total(), self.on_change() if self.on_change else None))
        def remove(rf=rf):
            for i, (p, a, r) in enumerate(self.rows):
                if r is rf:
                    self.rows.pop(i); rf.destroy(); self._update_total()
                    if self.on_change: self.on_change()
                    break
        if len(self.rows) > 0:
            tk.Button(inner, text="\u00d7", bg=row_bg, fg=DANGER, relief="flat", bd=0,
                      font=("Consolas", 12), cursor="hand2", padx=6, command=remove).pack(side="right", padx=(0, 4))
        self.rows.append((pur_ent, amt_ent, rf)); self._update_total()

    def _update_total(self):
        total = 0.0
        for p, a, r in self.rows:
            v = a.get().strip()
            if v not in ("", "0.00"):
                try: total += float(v)
                except: pass
        self.total_var.set(f"Total: Rs {total:,.2f}")

    def get_entries(self):
        result = []
        purpose_ph = "Purpose of expense"
        for p, a, r in self.rows:
            purpose = p.get().strip()
            if purpose == purpose_ph: purpose = ""
            amt = 0.0
            try:
                v = a.get().strip()
                if v not in ("", "0.00"): amt = float(v)
            except: pass
            if purpose or amt > 0:
                result.append((purpose if purpose else "Miscellaneous", amt))
        return result

    def get_total(self): return sum(amt for _, amt in self.get_entries())

    def reset(self):
        for p, a, r in self.rows: r.destroy()
        self.rows.clear(); self.add_row(); self._update_total()

    def load(self, entries):
        for p, a, r in self.rows: r.destroy()
        self.rows.clear()
        for purpose, amt in entries:
            self.add_row(default_purpose=purpose, default_amt=str(amt) if amt else "")
        if not entries: self.add_row()
        self._update_total()


# ══════════════════════════════════════════════════════════════════════════════
#  RECORD EDIT / VIEW / TREND / REPORT
# ══════════════════════════════════════════════════════════════════════════════

def edit_record(record_id, mode, root_ref, on_save_cb=None):
    tbl = "factory_records" if mode == "factory" else "parlor_records"
    c.execute(f"SELECT * FROM {tbl} WHERE id=?", (record_id,))
    row = c.fetchone()
    if not row: return

    c.execute(f"PRAGMA table_info({tbl})")
    col_names = [r[1] for r in c.fetchall()]
    row_dict  = dict(zip(col_names, row))

    win = tk.Toplevel(root_ref)
    win.title(f"Edit Record — ID {record_id}  [{mode.capitalize()}]")
    win.configure(bg=BG); win.resizable(True, True)
    sw, sh = root_ref.winfo_screenwidth(), root_ref.winfo_screenheight()
    w, h = min(700, int(sw*0.50)), min(900, int(sh*0.94))
    win.geometry(f"{w}x{h}+{sw//2-w//2}+{sh//2-h//2}")

    acc = FACTORY_AC if mode == "factory" else ACCENT
    tk.Frame(win, bg=acc, height=2).pack(fill="x")
    hdr_f = tk.Frame(win, bg=SURFACE, pady=10); hdr_f.pack(fill="x")
    tk.Label(hdr_f, text=f"EDIT RECORD  \u00b7  ID {record_id}  \u00b7  {mode.upper()}",
             bg=SURFACE, fg=TEXT, font=FONT_HEAD).pack(padx=20, anchor="w")
    tk.Label(hdr_f, text="All changes will overwrite the existing record.",
             bg=SURFACE, fg=TEXT3, font=FONT_BRAND).pack(padx=20, anchor="w")
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")

    inner_scroll = scrollable_frame(win, bg=SURFACE)
    pad = tk.Frame(inner_scroll, bg=SURFACE, padx=24, pady=16); pad.pack(fill="both", expand=True)

    entries = {}

    section_hdr(pad, "  DATE")
    dr = tk.Frame(pad, bg=SURFACE); dr.pack(fill="x", pady=3)
    tk.Label(dr, text="Date", bg=SURFACE, fg=TEXT3, font=FONT_LABEL).pack(anchor="w")
    df, e_date = styled_entry(dr, "DD-MM-YYYY"); df.pack(fill="x", pady=(2,0))
    e_date.delete(0, tk.END); e_date.insert(0, row_dict.get("date", "")); e_date.config(fg=TEXT2)
    entries["date"] = e_date

    _, e_ob = form_row(pad, "Opening Balance (Rs)", str(row_dict.get("opening_balance", 0)), "\u2014", SURFACE)
    entries["opening_balance"] = e_ob

    section_hdr(pad, "  SALARY & ALLOWANCES")
    sal_w = SalaryWidget(pad, bg=SURFACE)
    c.execute("SELECT employee_name, amount FROM salary_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    sal_rows = c.fetchall()
    if sal_rows: sal_w.load(sal_rows)

    section_hdr(pad, "  VEHICLE EXPENSES")
    veh_w = VehicleWidget(pad, bg=SURFACE)
    c.execute("SELECT vehicle_number, petrol, maintenance FROM vehicle_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    veh_rows = c.fetchall()
    if veh_rows: veh_w.load(veh_rows)

    section_hdr(pad, "  MISCELLANEOUS EXPENSES")
    misc_w = MiscWidget(pad, bg=SURFACE)
    c.execute("SELECT purpose, amount FROM misc_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    misc_rows = c.fetchall()
    if misc_rows: misc_w.load(misc_rows)

    section_hdr(pad, "  MILK EXPENSES")
    _, e_milk = form_row(pad, "Milk Expense (Rs)", str(row_dict.get("milk_expenses", 0)), "\u25cf", SURFACE)
    entries["milk_expenses"] = e_milk

    section_hdr(pad, "  KEB ELECTRICITY  (CUSTOMISABLE METERS)")
    keb_w = KEBWidget(pad, bg=SURFACE)
    c.execute("SELECT meter_name, amount FROM keb_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    keb_rows = c.fetchall()
    if keb_rows:
        keb_dict = {m: a for m, a in keb_rows}
        keb_w.load(keb_dict)
    else:
        # Fallback: load legacy honnavar/ramthirth columns if keb_entries are empty
        hon = row_dict.get("keb_honnaver", 0); ram = row_dict.get("keb_ramthirth", 0)
        legacy = {}
        if hon: legacy["Honnavar Meter"] = hon
        if ram: legacy["Ramthirth Meter"] = ram
        if legacy: keb_w.load(legacy)

    section_hdr(pad, "  PURCHASES")
    _, entries["ice_cream_purchases"] = form_row(pad, "Ice Cream Purchases (Rs)", str(row_dict.get("ice_cream_purchases", 0)), "\u2014", SURFACE)
    section_hdr(pad, "  PIGMY / SAVINGS")
    _, entries["pigmy"] = form_row(pad, "Pigmy Deposit (Rs)", str(row_dict.get("pigmy", 0)), "\u25c8", SURFACE)

    status_var = tk.StringVar()
    tk.Frame(pad, bg=BORDER, height=1).pack(fill="x", pady=(16,8))
    btn_row = tk.Frame(pad, bg=SURFACE); btn_row.pack(fill="x")

    def do_save():
        g = lambda k: get_float(entries[k]) if k in entries else 0.0
        date_v = entries["date"].get().strip()
        if not date_v:
            messagebox.showerror("Missing", "Date is required.", parent=win); return

        if date_exists(date_v, mode, exclude_id=record_id):
            messagebox.showerror("Duplicate Date",
                f"A {mode} record for {date_v} already exists.\nPlease use a different date.", parent=win)
            return

        ob   = g("opening_balance"); milk = g("milk_expenses")
        sal  = sal_w.get_total()
        pet  = veh_w.get_total_petrol(); vm = veh_w.get_total_maint()
        keb  = keb_w.get_total(); misc = misc_w.get_total()
        keb_vals = keb_w.get_all_values()
        keb_hon  = sum(v for k, v in keb_vals.items() if "Honnavar" in k)
        keb_ram  = sum(v for k, v in keb_vals.items() if "Ramthirth" in k)

        icp = g("ice_cream_purchases"); pig = g("pigmy")
        total_exp = sal + pet + vm + misc + keb + milk
        day_sales = (total_exp + icp + pig) - ob

        tbl2 = "factory_records" if mode == "factory" else "parlor_records"
        c.execute(f"""UPDATE {tbl2} SET date=?,opening_balance=?,misc_expenses=?,
            ice_cream_purchases=?,keb_honnaver=?,keb_ramthirth=?,pigmy=?,
            milk_expenses=?,day_sales=? WHERE id=?""",
            (date_v, ob, misc, icp, keb_hon, keb_ram, pig, milk, day_sales, record_id))
        conn.commit()

        for sub_tbl in ("salary_entries", "vehicle_entries", "misc_entries", "keb_entries"):
            c.execute(f"DELETE FROM {sub_tbl} WHERE record_id=? AND record_type=?", (record_id, mode))
        for emp, amt in sal_w.get_entries():
            c.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                      (record_id, mode, emp, amt))
        for vno, pet2, maint in veh_w.get_entries():
            c.execute("INSERT INTO vehicle_entries (record_id,record_type,vehicle_number,petrol,maintenance) VALUES (?,?,?,?,?)",
                      (record_id, mode, vno, pet2, maint))
        for purpose, amt in misc_w.get_entries():
            c.execute("INSERT INTO misc_entries (record_id,record_type,purpose,amount) VALUES (?,?,?,?)",
                      (record_id, mode, purpose, amt))
        for meter, amt in keb_vals.items():
            if amt > 0:
                c.execute("INSERT INTO keb_entries (record_id,record_type,meter_name,amount) VALUES (?,?,?,?)",
                          (record_id, mode, meter, amt))
        conn.commit()
        status_var.set(f"\u2713  Saved!  Day Sales = Rs {day_sales:,.2f}")
        if on_save_cb: on_save_cb()
        win.after(1500, win.destroy)

    make_button(btn_row, "  Save Changes  ", do_save,
                color=SUCCESS_BG, hover=MUTED, fg=SUCCESS, padx=18, pady=10).pack(side="left", fill="x", expand=True, padx=(0,6))
    make_button(btn_row, "  Cancel  ", win.destroy,
                color=SURFACE2, hover=SURFACE3, fg=TEXT3, padx=18, pady=10).pack(side="left")
    tk.Label(pad, textvariable=status_var, bg=SURFACE, fg=SUCCESS, font=("Consolas", 9)).pack(pady=(8,0), anchor="w")



def show_trend(mode, root_ref):
    is_factory = mode == "factory"
    tbl = "factory_records" if is_factory else "parlor_records"
    c.execute(f"""SELECT r.id, r.date, r.opening_balance,
                 r.misc_expenses, r.ice_cream_purchases,
                 r.keb_honnaver, r.keb_ramthirth,
                 r.pigmy, r.milk_expenses, r.day_sales
                 FROM {tbl} r ORDER BY r.id ASC""")
    rows = c.fetchall()
    if not rows:
        messagebox.showinfo("No Data", "No records found.", parent=root_ref); return

    dates, profits, expenses, purchases, salaries, day_sales_list = [], [], [], [], [], []
    for row in rows:
        try: dt = datetime.strptime(row[1], "%d-%m-%Y")
        except:
            try: dt = datetime.strptime(row[1], "%Y-%m-%d")
            except: continue
        dates.append(dt)
        rid = row[0]; ob = row[2]; milk = row[-2]; ds = row[-1] or 0.0

        c.execute("SELECT SUM(amount) FROM keb_entries WHERE record_id=? AND record_type=?", (rid, mode))
        keb_res = c.fetchone(); keb = keb_res[0] or 0.0
        if keb == 0.0: keb = (row[5] or 0) + (row[6] or 0)

        c.execute("SELECT SUM(amount) FROM misc_entries WHERE record_id=? AND record_type=?", (rid, mode))
        misc_res = c.fetchone(); misc_total = misc_res[0] or 0.0
        if misc_total == 0.0: misc_total = row[3] or 0.0

        c.execute("SELECT SUM(amount) FROM salary_entries WHERE record_id=? AND record_type=?", (rid, mode))
        sal_res = c.fetchone(); sal = sal_res[0] or 0.0

        c.execute("SELECT SUM(petrol), SUM(maintenance) FROM vehicle_entries WHERE record_id=? AND record_type=?", (rid, mode))
        veh_res = c.fetchone(); pet = veh_res[0] or 0.0; vm = veh_res[1] or 0.0

        icp = row[4]; pig = row[7]
        total_exp = sal + pet + vm + misc_total + keb + milk
        total_pur = icp

        expenses.append(total_exp); purchases.append(total_pur); salaries.append(sal)
        profits.append(-ob - total_exp - total_pur - pig)
        day_sales_list.append(ds)

    win = tk.Toplevel(root_ref)
    win.title(f"Trend Analysis \u2014 {'Factory' if is_factory else 'Parlour'}")
    win.configure(bg=BG)
    try: win.state("zoomed")
    except: win.attributes("-zoomed", True)

    acc = FACTORY_AC if is_factory else ACCENT
    tk.Frame(win, bg=acc, height=2).pack(fill="x")
    hdr = tk.Frame(win, bg=SURFACE); hdr.pack(fill="x")
    hl = tk.Frame(hdr, bg=SURFACE, padx=20, pady=12); hl.pack(side="left")
    tk.Label(hl, text=f"TREND ANALYSIS  \u00b7  {'FACTORY' if is_factory else 'PARLOUR'} MODE",
             bg=SURFACE, fg=TEXT, font=FONT_HEAD).pack(anchor="w")
    period = f"{dates[0].strftime('%d %b %Y')}  \u2192  {dates[-1].strftime('%d %b %Y')}" if dates else "\u2014"
    tk.Label(hl, text=f"{len(dates)} records  \u00b7  {period}", bg=SURFACE, fg=TEXT3, font=FONT_BRAND).pack(anchor="w")

    strip = tk.Frame(hdr, bg=SURFACE); strip.pack(side="right", padx=20, pady=12)
    def kpi(lbl, val, col=TEXT2):
        f = tk.Frame(strip, bg=SURFACE2, padx=14, pady=8); f.pack(side="left", padx=4)
        tk.Label(f, text=lbl, bg=SURFACE2, fg=TEXT3, font=FONT_SMALL).pack(anchor="center")
        tk.Label(f, text=val, bg=SURFACE2, fg=col, font=FONT_STAT).pack(anchor="center")
    kpi("Avg Expenses",   f"Rs {sum(expenses)/len(expenses):,.0f}" if expenses else "\u2014", INFO)
    kpi("Avg Day Sales",  f"Rs {sum(day_sales_list)/len(day_sales_list):,.0f}" if day_sales_list else "\u2014", WARNING)
    kpi("Total Purchases",f"Rs {sum(purchases):,.0f}", CH_PURCHASE)
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")

    tab_bar = tk.Frame(win, bg=BG2); tab_bar.pack(fill="x")
    chart_area = tk.Frame(win, bg=BG2); chart_area.pack(fill="both", expand=True)
    tab_btns = {}
    tabs = [("overview","  Overview  "),("daysales","  Day Sales  "),
            ("compare","  Expense Breakdown  "),("bars","  Bar Comparison  ")]

    def show_tab(key):
        for k, b in tab_btns.items():
            b.config(bg=SURFACE if k==key else BG2, fg=TEXT if k==key else TEXT3)
        for w in chart_area.winfo_children(): w.destroy()
        _draw(key)

    for key, label in tabs:
        b = tk.Button(tab_bar, text=label, font=FONT_BTN, bg=BG2, fg=TEXT3,
                      relief="flat", bd=0, padx=4, pady=10, cursor="hand2",
                      command=lambda k=key: show_tab(k))
        b.pack(side="left"); tab_btns[key] = b

    active_figs = []

    def _draw(key):
        for f in active_figs:
            try: plt.close(f)
            except: pass
        active_figs.clear()
        figsize = (14, 7)
        fmt = ticker.FuncFormatter(lambda x,_: f"Rs{x/1000:.0f}k" if abs(x)>=1000 else f"Rs{x:.0f}")

        if key == "overview":
            fig, axes = plt.subplots(2, 2, figsize=figsize, facecolor="#111111")
            fig.subplots_adjust(hspace=0.5, wspace=0.32, left=0.07, right=0.97, top=0.93, bottom=0.1)
            ax1,ax2,ax3,ax4 = axes[0][0],axes[0][1],axes[1][0],axes[1][1]
            for ax in [ax1,ax2,ax3,ax4]: apply_chart_style(ax, fig)
            ax1.plot(dates, expenses, color=CH_EXPENSE, lw=2, marker="s", ms=3, zorder=3)
            ax1.fill_between(dates, expenses, alpha=0.1, color=CH_EXPENSE); ax1.set_title("Daily Expenses")
            ax2.plot(dates, day_sales_list, color=WARNING, lw=2, marker="D", ms=4, zorder=3)
            ax2.fill_between(dates, day_sales_list, alpha=0.1, color=WARNING)
            ax2.axhline(0, color=BORDER2, lw=0.8); ax2.set_title("Day Sales")
            ax3.plot(dates, purchases, color=CH_PURCHASE, lw=2, marker="^", ms=3, zorder=3)
            ax3.fill_between(dates, purchases, alpha=0.1, color=CH_PURCHASE); ax3.set_title("Purchases")
            ax4.plot(dates, salaries, color=CH_SALARY, lw=2, marker="o", ms=4, zorder=3)
            ax4.fill_between(dates, salaries, alpha=0.1, color=CH_SALARY); ax4.set_title("Salary")
            for ax in [ax1,ax2,ax3,ax4]:
                ax.yaxis.set_major_formatter(fmt)
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=7)

        elif key == "daysales":
            fig, ax = plt.subplots(figsize=figsize, facecolor="#111111")
            fig.subplots_adjust(left=0.08, right=0.97, top=0.9, bottom=0.12)
            apply_chart_style(ax, fig)
            bc = [WARNING if d >= 0 else DANGER for d in day_sales_list]
            ax.bar(dates, day_sales_list, color=bc, width=0.6, alpha=0.85, zorder=3)
            ax.axhline(0, color=BORDER2, lw=1)
            if len(day_sales_list) >= 3:
                ma = [sum(day_sales_list[max(0,i-2):i+1])/len(day_sales_list[max(0,i-2):i+1]) for i in range(len(day_sales_list))]
                ax.plot(dates, ma, color=INFO, lw=1.5, ls="--", label="3-day avg", zorder=4)
                ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT2, fontsize=8)
            ax.set_title("Day Sales  =  All Expenses (incl. Purchases & Pigmy) \u2212 Opening Balance", fontsize=10)
            ax.yaxis.set_major_formatter(fmt)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=8)

        elif key == "compare":
            fig, (ax_l, ax_p) = plt.subplots(1, 2, figsize=figsize, facecolor="#111111")
            fig.subplots_adjust(left=0.06, right=0.97, top=0.9, bottom=0.12, wspace=0.3)
            apply_chart_style(ax_l, fig); ax_p.set_facecolor("#161616")
            ax_l.plot(dates, expenses,       color=CH_EXPENSE, lw=2, marker="s", ms=3, label="Expenses")
            ax_l.plot(dates, purchases,      color=CH_PURCHASE,lw=1.5,marker="^",ms=3, label="Purchases")
            ax_l.plot(dates, salaries,       color=CH_SALARY,  lw=1.5,marker="D",ms=3, label="Salary")
            ax_l.plot(dates, day_sales_list, color=WARNING,    lw=1.5,marker="*",ms=5, label="Day Sales")
            ax_l.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT2, fontsize=8)
            ax_l.set_title("Trend Comparison")
            ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
            ax_l.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax_l.get_xticklabels(), rotation=35, ha="right", fontsize=8)
            ax_l.yaxis.set_major_formatter(fmt)
            c.execute(f"""SELECT SUM(s.amount), SUM(v.petrol), SUM(v.maintenance),
                         SUM(r.misc_expenses), SUM(r.keb_honnaver+r.keb_ramthirth),
                         SUM(r.ice_cream_purchases), SUM(r.pigmy), SUM(r.milk_expenses)
                         FROM {tbl} r
                         LEFT JOIN salary_entries s ON s.record_id=r.id AND s.record_type=?
                         LEFT JOIN vehicle_entries v ON v.record_id=r.id AND v.record_type=?""",
                     (mode, mode))
            sums = c.fetchone(); pie_labs = ["Salary","Petrol","Veh Maint","Misc","KEB","Ice Cream","Pigmy","Milk"]
            pie_data = [(v or 0, l) for v,l in zip(sums, pie_labs) if (v or 0) > 0]
            if pie_data:
                vals2=[x[0] for x in pie_data]; labs2=[x[1] for x in pie_data]
                pie_cols=[CH_SALARY,CH_PURCHASE,CH_VEHICLE,CH_CLOSING,CH_SALES,CH_PROFIT,"#E8C4A0","#C4E8C4"]
                wedges,texts,autotexts = ax_p.pie(vals2,labels=labs2,autopct="%1.0f%%",
                    colors=pie_cols[:len(vals2)],pctdistance=0.8,startangle=90,
                    wedgeprops=dict(edgecolor="#111111",linewidth=1.2))
                for t in texts: t.set_color(TEXT3); t.set_fontsize(8)
                for t in autotexts: t.set_color("#111111"); t.set_fontsize(7); t.set_fontweight("bold")
            ax_p.set_title("Total Expense Breakdown", fontsize=9, color=TEXT2, pad=10)

        elif key == "bars":
            fig, ax = plt.subplots(figsize=figsize, facecolor="#111111")
            fig.subplots_adjust(left=0.07, right=0.97, top=0.9, bottom=0.15)
            apply_chart_style(ax, fig)
            xi = np.arange(len(dates)); w = 0.22
            ax.bar(xi-w,   expenses,       width=w, color=CH_EXPENSE,  alpha=0.85, label="Expenses",  zorder=3)
            ax.bar(xi,     purchases,      width=w, color=CH_PURCHASE, alpha=0.85, label="Purchases", zorder=3)
            ax.bar(xi+w,   day_sales_list, width=w, color=WARNING,     alpha=0.85, label="Day Sales", zorder=3)
            ax.set_xticks(xi)
            ax.set_xticklabels([d.strftime("%d/%m") for d in dates], rotation=40, ha="right", fontsize=7)
            ax.legend(facecolor=SURFACE, edgecolor=BORDER, labelcolor=TEXT2, fontsize=8)
            ax.set_title("Expenses vs Purchases vs Day Sales", fontsize=10)
            ax.yaxis.set_major_formatter(fmt)

        active_figs.append(fig)
        cnv = FigureCanvasTkAgg(fig, master=chart_area)
        cnv.draw(); cnv.get_tk_widget().pack(fill="both", expand=True)

    show_tab("overview")
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
    bf = tk.Frame(win, bg=SURFACE, pady=8); bf.pack(fill="x")
    make_button(bf, "  Close  ", win.destroy, color=SURFACE2, hover=MUTED, pady=8).pack(side="right", padx=16, pady=4)



def show_report(mode, data, results, root_ref):
    win = tk.Toplevel(root_ref); win.title("Daily Financial Report")
    win.configure(bg=BG); win.resizable(True, True)
    sw, sh = root_ref.winfo_screenwidth(), root_ref.winfo_screenheight()
    w, h = min(580, int(sw*0.38)), min(860, int(sh*0.92))
    win.geometry(f"{w}x{h}+{sw//2-w//2}+{sh//2-h//2}")
    acc = FACTORY_AC if mode == "factory" else ACCENT
    tk.Frame(win, bg=acc, height=2).pack(fill="x")
    hdr = tk.Frame(win, bg=SURFACE, pady=12); hdr.pack(fill="x")
    mode_label = "ICE CREAM FACTORY" if mode == "factory" else "ICE CREAM PARLOUR"
    tk.Label(hdr, text=f"KARAVALI {mode_label}", bg=SURFACE, fg=TEXT, font=FONT_HEAD).pack(padx=20, anchor="w")
    tk.Label(hdr, text=f"DAILY FINANCIAL REPORT   \u00b7   {data['date']}",
             bg=SURFACE, fg=TEXT3, font=FONT_BRAND).pack(padx=20, anchor="w")
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
    sc = tk.Canvas(win, bg=BG, highlightthickness=0)
    sb2 = ttk.Scrollbar(win, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb2.set); sb2.pack(side="right", fill="y"); sc.pack(fill="both", expand=True)
    inn = tk.Frame(sc, bg=BG); cw2 = sc.create_window((0,0), window=inn, anchor="nw")
    inn.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<Configure>", lambda e: sc.itemconfig(cw2, width=e.width))
    pad = tk.Frame(inn, bg=BG); pad.pack(fill="both", expand=True, padx=24, pady=16)

    def rsec(t):
        tk.Frame(pad, bg=BORDER, height=1).pack(fill="x", pady=(10,0))
        f = tk.Frame(pad, bg=BG); f.pack(fill="x", pady=(4,4))
        tk.Label(f, text=t, bg=BG, fg=TEXT3, font=FONT_SECTION).pack(anchor="w")

    def rline(label, val, col=TEXT2, bold=False, indent=False):
        f = tk.Frame(pad, bg=BG); f.pack(fill="x", pady=2)
        prefix = "    \u21b3  " if indent else ""
        lbl_col = HIGHLIGHT if indent else TEXT3
        tk.Label(f, text=prefix+label, bg=BG, fg=lbl_col,
                 font=("Segoe UI", 8 if indent else (10 if bold else 9))).pack(side="left")
        tk.Label(f, text=val, bg=BG, fg=col,
                 font=("Consolas", 10, "bold") if bold else ("Consolas", 10 if not indent else 9)).pack(side="right")

    rsec("OPENING"); rline("Opening Balance", f"Rs {data['opening_balance']:,.2f}", WARNING)
    rsec("SALARY & ALLOWANCES")
    for emp, amt in data.get("salary_entries", []): rline(emp if emp else "Employee", f"Rs {amt:,.2f}", TEXT2, indent=True)
    rline("Total Salary", f"Rs {results['total_salary']:,.2f}", CH_SALARY, bold=True)
    rsec("VEHICLE EXPENSES")
    for vno, pet, maint in data.get("vehicle_entries", []):
        if pet > 0:   rline(f"Petrol  [{vno}]", f"Rs {pet:,.2f}", TEXT2, indent=True)
        if maint > 0: rline(f"Maint   [{vno}]", f"Rs {maint:,.2f}", TEXT2, indent=True)
    rline("Total Vehicle", f"Rs {results['total_vehicle']:,.2f}", CH_VEHICLE, bold=True)
    rsec("MISCELLANEOUS EXPENSES")
    for purpose, amt in data.get("misc_entries", []): rline(purpose, f"Rs {amt:,.2f}", TEXT2, indent=True)
    rline("Total Misc", f"Rs {results['total_misc']:,.2f}", WARNING, bold=True)
    rsec("MILK EXPENSES"); rline("Milk Expense", f"Rs {data.get('milk_expenses', 0):,.2f}", "#E8D5A0")
    rsec("KEB ELECTRICITY")
    # Show each meter individually (fully dynamic — no hardcoded list)
    keb_values = data.get("keb_values", {})
    for meter, val in keb_values.items():
        if val > 0: rline(meter, f"Rs {val:,.2f}", TEXT2, indent=True)
    rline("Total KEB", f"Rs {results['total_keb']:,.2f}", INFO, bold=True)
    tk.Frame(pad, bg=BORDER, height=1).pack(fill="x", pady=4)
    rline("Total Expenses", f"Rs {results['total_expenses']:,.2f}", DANGER, bold=True)
    rsec("PURCHASES")
    rline("Ice Cream Purchases", f"Rs {data.get('ice_cream_purchases', 0):,.2f}")
    rline("Total Purchases", f"Rs {results['total_purchases']:,.2f}", INFO, bold=True)
    rsec("PIGMY / SAVINGS"); rline("Pigmy Deposit", f"Rs {data.get('pigmy', 0):,.2f}", TEXT3)
    rsec("DAY SALES")
    ds = results["day_sales"]; ds_col = WARNING if ds >= 0 else DANGER
    ds_bg_frame = tk.Frame(pad, bg="#1A1500" if ds >= 0 else DANGER_BG); ds_bg_frame.pack(fill="x")
    ds_inner = tk.Frame(ds_bg_frame, bg=ds_bg_frame["bg"], padx=12, pady=10); ds_inner.pack(fill="x")
    tk.Label(ds_inner, text="DAY SALES  =  All Expenses (incl. Purchases & Pigmy) \u2212 Opening Balance",
             bg=ds_bg_frame["bg"], fg=TEXT3, font=FONT_SECTION).pack(anchor="w")
    tk.Label(ds_inner, text=f"Rs {ds:,.2f}",
             bg=ds_bg_frame["bg"], fg=ds_col, font=("Consolas", 18, "bold")).pack(anchor="w", pady=(4, 0))
    rsec("SUMMARY")
    rline("Total Cash Outflow", f"Rs {results['total_outflow']:,.2f}", DANGER)
    rline("Closing Balance",    f"Rs {results['closing_balance']:,.2f}", TEXT, bold=True)
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
    bf2 = tk.Frame(win, bg=SURFACE, pady=8); bf2.pack(fill="x")
    make_button(bf2, "  Close  ", win.destroy, color=SURFACE2, hover=MUTED, pady=8, width=10).pack(pady=4)



def view_record_detail(record_id, mode, root_ref):
    tbl = "factory_records" if mode == "factory" else "parlor_records"
    c.execute(f"SELECT * FROM {tbl} WHERE id=?", (record_id,))
    row = c.fetchone()
    if not row: return
    win = tk.Toplevel(root_ref); win.title(f"Record Detail — ID {record_id}")
    win.configure(bg=BG); win.resizable(True, True)
    sw, sh = root_ref.winfo_screenwidth(), root_ref.winfo_screenheight()
    w, h = min(560, int(sw*0.36)), min(820, int(sh*0.88))
    win.geometry(f"{w}x{h}+{sw//2-w//2}+{sh//2-h//2}")
    acc = FACTORY_AC if mode == "factory" else ACCENT
    tk.Frame(win, bg=acc, height=2).pack(fill="x")
    hdr = tk.Frame(win, bg=SURFACE, pady=10); hdr.pack(fill="x")
    tk.Label(hdr, text=f"RECORD DETAIL  \u00b7  ID {record_id}", bg=SURFACE, fg=TEXT, font=FONT_HEAD).pack(padx=20, anchor="w")
    c.execute(f"PRAGMA table_info({tbl})")
    col_info = [r[1] for r in c.fetchall()]; row_dict = dict(zip(col_info, row))
    tk.Label(hdr, text=f"{row_dict.get('date','')}", bg=SURFACE, fg=TEXT3, font=FONT_BRAND).pack(padx=20, anchor="w")
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
    sc = tk.Canvas(win, bg=BG, highlightthickness=0)
    sb2 = ttk.Scrollbar(win, orient="vertical", command=sc.yview)
    sc.configure(yscrollcommand=sb2.set); sb2.pack(side="right", fill="y"); sc.pack(fill="both", expand=True)
    inn = tk.Frame(sc, bg=BG); cw2 = sc.create_window((0,0), window=inn, anchor="nw")
    inn.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
    sc.bind("<Configure>", lambda e: sc.itemconfig(cw2, width=e.width))
    pad = tk.Frame(inn, bg=BG); pad.pack(fill="both", expand=True, padx=24, pady=14)

    def dsec(t):
        tk.Frame(pad, bg=BORDER, height=1).pack(fill="x", pady=(8,0))
        f = tk.Frame(pad, bg=BG); f.pack(fill="x", pady=(4,4))
        tk.Label(f, text=t, bg=BG, fg=TEXT3, font=FONT_SECTION).pack(anchor="w")

    def dline(label, val, col=TEXT2, indent=False):
        f = tk.Frame(pad, bg=BG); f.pack(fill="x", pady=2)
        prefix = "    \u21b3  " if indent else ""
        lc = HIGHLIGHT if indent else TEXT3
        tk.Label(f, text=prefix+label, bg=BG, fg=lc, font=("Segoe UI", 8 if indent else 9)).pack(side="left")
        tk.Label(f, text=val, bg=BG, fg=col, font=("Consolas", 9 if indent else 10)).pack(side="right")

    dsec("BASIC INFO"); dline("Date", row_dict.get("date",""), TEXT2)
    dline("Opening Balance", f"Rs {row_dict.get('opening_balance',0):,.2f}", WARNING)

    dsec("SALARY & ALLOWANCES")
    c.execute("SELECT employee_name, amount FROM salary_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    sal_rows = c.fetchall(); sal_total = 0.0
    if sal_rows:
        for emp, amt in sal_rows: dline(emp if emp else "Employee", f"Rs {amt:,.2f}", TEXT2, indent=True); sal_total += amt
    else: tk.Label(pad, text="  No salary entries", bg=BG, fg=TEXT4, font=FONT_SMALL).pack(anchor="w")
    dline("Total Salary", f"Rs {sal_total:,.2f}", CH_SALARY)

    dsec("VEHICLE EXPENSES")
    c.execute("SELECT vehicle_number, petrol, maintenance FROM vehicle_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    veh_rows = c.fetchall(); veh_total = 0.0
    if veh_rows:
        for vno, pet, maint in veh_rows:
            if pet > 0:   dline(f"Petrol [{vno}]", f"Rs {pet:,.2f}", TEXT2, indent=True); veh_total += pet
            if maint > 0: dline(f"Maint  [{vno}]", f"Rs {maint:,.2f}", TEXT2, indent=True); veh_total += maint
    else: tk.Label(pad, text="  No vehicle entries", bg=BG, fg=TEXT4, font=FONT_SMALL).pack(anchor="w")
    dline("Total Vehicle", f"Rs {veh_total:,.2f}", CH_VEHICLE)

    dsec("MISCELLANEOUS EXPENSES")
    c.execute("SELECT purpose, amount FROM misc_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    misc_rows = c.fetchall(); misc_total = 0.0
    if misc_rows:
        for purpose, amt in misc_rows: dline(purpose if purpose else "Misc", f"Rs {amt:,.2f}", TEXT2, indent=True); misc_total += amt
    else:
        misc_total = row_dict.get("misc_expenses", 0)
        if misc_total > 0: dline("Miscellaneous", f"Rs {misc_total:,.2f}", TEXT2, indent=True)
        else: tk.Label(pad, text="  No misc entries", bg=BG, fg=TEXT4, font=FONT_SMALL).pack(anchor="w")
    dline("Total Misc", f"Rs {misc_total:,.2f}", WARNING)

    dsec("MILK EXPENSES"); dline("Milk Expense", f"Rs {row_dict.get('milk_expenses',0):,.2f}", "#E8D5A0")

    dsec("KEB ELECTRICITY")
    c.execute("SELECT meter_name, amount FROM keb_entries WHERE record_id=? AND record_type=? ORDER BY id", (record_id, mode))
    keb_rows = c.fetchall(); keb_total = 0.0
    if keb_rows:
        for meter, amt in keb_rows:
            if amt > 0: dline(meter, f"Rs {amt:,.2f}", TEXT2, indent=True); keb_total += amt
    else:
        # Legacy fallback
        hon = row_dict.get("keb_honnaver", 0); ram = row_dict.get("keb_ramthirth", 0)
        keb_total = hon + ram
        if hon > 0: dline("Honnavar Meter (legacy)", f"Rs {hon:,.2f}", TEXT2, indent=True)
        if ram > 0: dline("Ramthirth Meter (legacy)", f"Rs {ram:,.2f}", TEXT2, indent=True)
        if keb_total == 0: tk.Label(pad, text="  No KEB entries", bg=BG, fg=TEXT4, font=FONT_SMALL).pack(anchor="w")
    dline("Total KEB", f"Rs {keb_total:,.2f}", INFO)

    dsec("PURCHASES"); dline("Ice Cream Purchases", f"Rs {row_dict.get('ice_cream_purchases',0):,.2f}", INFO)
    dsec("PIGMY / SAVINGS"); dline("Pigmy Deposit", f"Rs {row_dict.get('pigmy',0):,.2f}", TEXT3)

    dsec("DAY SALES")
    ds = row_dict.get("day_sales", 0); ds_col = WARNING if ds >= 0 else DANGER
    dline("Day Sales  (All Expenses incl. Purchases \u2212 Opening Bal)", f"Rs {ds:,.2f}", ds_col)
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
    bf = tk.Frame(win, bg=SURFACE, pady=8); bf.pack(fill="x")
    make_button(bf, "  Close  ", win.destroy, color=SURFACE2, hover=MUTED, pady=7, width=10).pack(pady=4)



def view_all_records(mode, root_ref):
    win = tk.Toplevel(root_ref)
    win.title(f"All Records \u2014 {'Factory' if mode=='factory' else 'Parlour'}")
    win.configure(bg=BG)
    sw, sh = root_ref.winfo_screenwidth(), root_ref.winfo_screenheight()
    win.geometry(f"{min(1380, int(sw*0.92))}x{min(700, int(sh*0.82))}")
    acc = FACTORY_AC if mode == "factory" else ACCENT
    tk.Frame(win, bg=acc, height=2).pack(fill="x")
    hdr = tk.Frame(win, bg=SURFACE, pady=12); hdr.pack(fill="x")
    tk.Label(hdr, text=f"  ALL {'FACTORY' if mode=='factory' else 'PARLOUR'} RECORDS",
             bg=SURFACE, fg=TEXT, font=FONT_HEAD).pack(side="left", padx=20)
    tbl = "factory_records" if mode=="factory" else "parlor_records"
    c.execute(f"SELECT COUNT(*) FROM {tbl}")
    cnt = c.fetchone()[0]
    tk.Label(hdr, text=f"Entries: {cnt}   \u00b7   Double-click: detail   \u00b7   Select row then Edit or Delete",
             bg=SURFACE, fg=TEXT3, font=FONT_BRAND).pack(side="right", padx=20)
    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")

    s = ttk.Style(); s.theme_use("clam")
    s.configure("K.Treeview", background=SURFACE2, foreground=TEXT2,
                rowheight=30, fieldbackground=SURFACE2, borderwidth=0, font=("Consolas", 9))
    s.configure("K.Treeview.Heading", background=SURFACE, foreground=TEXT3,
                font=("Segoe UI Semibold", 9), relief="flat")
    s.map("K.Treeview", background=[("selected", MUTED)], foreground=[("selected", TEXT)])

    cols   = ("ID","Date","Opening","Salary","Petrol","VehMaint","Misc","Milk","IceCream","KEB","Pigmy","DaySales")
    widths = (40, 95, 90, 85, 72, 82, 75, 75, 95, 80, 75, 90)

    frm = tk.Frame(win, bg=BG); frm.pack(fill="both", expand=True, padx=12, pady=8)
    sb2 = ttk.Scrollbar(frm, orient="vertical"); sb2.pack(side="right", fill="y")
    sbh = ttk.Scrollbar(frm, orient="horizontal"); sbh.pack(side="bottom", fill="x")
    tree = ttk.Treeview(frm, columns=cols, show="headings", style="K.Treeview",
                        yscrollcommand=sb2.set, xscrollcommand=sbh.set)
    sb2.config(command=tree.yview); sbh.config(command=tree.xview)
    for col, w in zip(cols, widths):
        tree.heading(col, text=col); tree.column(col, width=w, anchor="center")

    def load_tree():
        for item in tree.get_children(): tree.delete(item)
        c.execute(f"""SELECT id,date,opening_balance,misc_expenses,
                     ice_cream_purchases,keb_honnaver,keb_ramthirth,pigmy,milk_expenses,day_sales
                     FROM {tbl} ORDER BY id DESC""")
        for row in c.fetchall():
            rid=row[0]; ob=row[2]; icp=row[4]; pig=row[7]; milk=row[8]; ds=row[9] or 0
            c.execute(f"SELECT SUM(amount) FROM salary_entries WHERE record_id=? AND record_type=?", (rid, mode))
            sal = (c.fetchone()[0] or 0)
            c.execute(f"SELECT SUM(petrol), SUM(maintenance) FROM vehicle_entries WHERE record_id=? AND record_type=?", (rid, mode))
            vr = c.fetchone(); pet = vr[0] or 0; vm = vr[1] or 0
            c.execute(f"SELECT SUM(amount) FROM misc_entries WHERE record_id=? AND record_type=?", (rid, mode))
            misc_r = c.fetchone(); misc_total = misc_r[0] or 0
            if misc_total == 0: misc_total = row[3] or 0
            c.execute(f"SELECT SUM(amount) FROM keb_entries WHERE record_id=? AND record_type=?", (rid, mode))
            keb_r = c.fetchone(); keb = keb_r[0] or 0
            if keb == 0: keb = (row[5] or 0) + (row[6] or 0)
            vals = (rid, row[1], f"Rs{ob:,.0f}", f"Rs{sal:,.0f}",
                    f"Rs{pet:,.0f}", f"Rs{vm:,.0f}", f"Rs{misc_total:,.0f}",
                    f"Rs{milk:,.0f}", f"Rs{icp:,.0f}", f"Rs{keb:,.0f}",
                    f"Rs{pig:,.0f}", f"Rs{ds:,.0f}")
            tree.insert("", tk.END, values=vals, iid=str(rid))

    load_tree()
    tree.pack(fill="both", expand=True)

    def on_double_click(event):
        item = tree.focus()
        if item:
            try: view_record_detail(int(item), mode, win)
            except: pass
    tree.bind("<Double-1>", on_double_click)

    tk.Frame(win, bg=BORDER, height=1).pack(fill="x")
    info_f = tk.Frame(win, bg=SURFACE, pady=6); info_f.pack(fill="x")
    tk.Label(info_f, text="  \u2139  DaySales = All Expenses (incl. Purchases & Pigmy) \u2212 Opening Balance   \u00b7   Double-click for full detail",
             bg=SURFACE, fg=TEXT3, font=FONT_SMALL).pack(side="left", padx=16)

    def do_edit():
        item = tree.focus()
        if not item:
            messagebox.showinfo("Select Row", "Please click a row to select it first.", parent=win); return
        try: edit_record(int(item), mode, win, on_save_cb=load_tree)
        except: pass

    def do_delete():
        item = tree.focus()
        if not item:
            messagebox.showinfo("Select Row", "Please click a row to select it first.", parent=win); return
        try:
            rid = int(item)
            c.execute(f"SELECT date FROM {tbl} WHERE id=?", (rid,))
            row2 = c.fetchone()
            date_str = row2[0] if row2 else f"ID {rid}"
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Permanently delete the {mode} record for  {date_str}?\n\n"
                "This will also remove all salary, vehicle, misc and KEB entries for this record.\n\n"
                "This action cannot be undone.",
                icon="warning", parent=win)
            if not confirm: return
            for sub in ("salary_entries", "vehicle_entries", "misc_entries", "keb_entries"):
                c.execute(f"DELETE FROM {sub} WHERE record_id=? AND record_type=?", (rid, mode))
            c.execute(f"DELETE FROM {tbl} WHERE id=?", (rid,))
            conn.commit()
            load_tree()
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=win)

    bf = tk.Frame(win, bg=SURFACE, pady=8); bf.pack(fill="x")
    make_button(bf, "  \u270e  Edit Selected  ", do_edit,
                color=SURFACE3, hover=MUTED, fg=WARNING, padx=16, pady=8).pack(side="left", padx=(16,6), pady=4)
    make_button(bf, "  \u2715  Delete Selected  ", do_delete,
                color=DANGER_BG, hover=MUTED, fg=DANGER, padx=16, pady=8).pack(side="left", padx=(0,6), pady=4)
    make_button(bf, "  Close  ", win.destroy,
                color=SURFACE2, hover=MUTED, pady=8, width=10).pack(side="right", padx=16, pady=4)



class KaravaliApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KARAVALI \u2014 Financial Management System")
        self.root.configure(bg=BG)
        try: self.root.state("zoomed")
        except: self.root.attributes("-zoomed", True)
        self.root.minsize(900, 650)
        self.mode = tk.StringVar(value="parlor")
        self.entries = {}; self.status_var = tk.StringVar()
        self.salary_widget = self.vehicle_widget = self.keb_widget = self.misc_widget = None
        self._build_topbar(); self._build_main(); self._build_footer()

        show_password_screen(self.root, self.switch_mode)

    def _build_topbar(self):
        self.tb = tk.Frame(self.root, bg=SURFACE); self.tb.pack(fill="x")
        self.accent_bar = tk.Frame(self.tb, bg=ACCENT, width=4); self.accent_bar.pack(side="left", fill="y")
        left = tk.Frame(self.tb, bg=SURFACE, padx=20, pady=14); left.pack(side="left")
        self.title_lbl = tk.Label(left, text="KARAVALI ICE CREAM PARLOUR", bg=SURFACE, fg=TEXT, font=FONT_HEAD)
        self.title_lbl.pack(anchor="w")
        self.sub_lbl = tk.Label(left, text="Daily Financial Management System  \u00b7  Parlour Mode",
                                bg=SURFACE, fg=TEXT3, font=FONT_BRAND)
        self.sub_lbl.pack(anchor="w")
        right = tk.Frame(self.tb, bg=SURFACE, padx=20, pady=14); right.pack(side="right")
        tk.Label(right, text=datetime.now().strftime("%A, %d %B %Y"),
                 bg=SURFACE, fg=TEXT3, font=FONT_BRAND).pack(anchor="e")
        mode_f = tk.Frame(right, bg=SURFACE, pady=6); mode_f.pack(anchor="e")
        tk.Label(mode_f, text="MODE", bg=SURFACE, fg=TEXT3, font=FONT_SECTION).pack(side="left", padx=(0,8))
        s = ttk.Style(); s.theme_use("clam")
        s.configure("K.TCombobox", fieldbackground=SURFACE3, background=SURFACE3,
                    foreground=TEXT, selectbackground=MUTED, selectforeground=TEXT,
                    bordercolor=BORDER2, arrowcolor=TEXT3, relief="flat")
        s.map("K.TCombobox", fieldbackground=[("readonly", SURFACE3)],
              background=[("readonly", SURFACE3)], foreground=[("readonly", TEXT)])
        self.mode_combo = ttk.Combobox(mode_f, textvariable=self.mode,
                                       values=["parlor","factory"], state="readonly",
                                       width=11, font=("Consolas",10), style="K.TCombobox")
        self.mode_combo.pack(side="left")
        self.mode_combo.bind("<<ComboboxSelected>>", lambda e: self.switch_mode())
        self.accent_line = tk.Frame(self.root, bg=ACCENT, height=2); self.accent_line.pack(fill="x")

    def _build_main(self):
        self.main = tk.Frame(self.root, bg=BG); self.main.pack(fill="both", expand=True)
        self.left_col = tk.Frame(self.main, bg=BG); self.left_col.pack(side="left", fill="both", expand=True)
        self.right_col = tk.Frame(self.main, bg=BG2); self.right_col.pack(side="right", fill="y")
        def _resize(e=None):
            sw = self.root.winfo_screenwidth()
            self.right_col.config(width=max(220, min(280, int(sw*0.18))))
        self.right_col.pack_propagate(False)
        self.root.after(100, _resize); self.root.bind("<Configure>", _resize)
        self._build_right_panel()

    def _build_right_panel(self):
        self.net_card = tk.Frame(self.right_col, bg=BG2); self.net_card.pack(fill="x")
        tk.Frame(self.net_card, bg=BORDER, height=1).pack(fill="x")
        self.net_inner = tk.Frame(self.net_card, bg=BG2, padx=18, pady=20); self.net_inner.pack(fill="both")
        self.net_title = tk.Label(self.net_inner, text="DAY SALES", bg=BG2, fg=TEXT3, font=FONT_SECTION)
        self.net_title.pack(anchor="w")
        self.net_var = tk.StringVar(value="Rs 0.00")
        self.net_label = tk.Label(self.net_inner, textvariable=self.net_var, bg=BG2, fg=WARNING, font=FONT_NET)
        self.net_label.pack(anchor="w", pady=(8,2))
        self.net_sub = tk.Label(self.net_inner, text="All Expenses (incl. Purchases) \u2212 Opening Bal", bg=BG2, fg=TEXT4, font=FONT_SMALL)
        self.net_sub.pack(anchor="w")
        tk.Frame(self.net_inner, bg=BORDER, height=1).pack(fill="x", pady=10)
        self.net_badge = tk.Label(self.net_inner, text="\u25b2 POSITIVE", bg=BG2, fg=WARNING, font=FONT_SECTION)
        self.net_badge.pack(anchor="w")
        tk.Frame(self.net_inner, bg=BORDER, height=1).pack(fill="x", pady=(10,4))
        self.breakdown_frame = tk.Frame(self.net_inner, bg=BG2); self.breakdown_frame.pack(fill="x")
        tk.Frame(self.right_col, bg=BORDER, height=1).pack(fill="x", pady=(12,0))
        self.stats_outer = tk.Frame(self.right_col, bg=BG2, padx=18, pady=14); self.stats_outer.pack(fill="x")
        self._refresh_stats()

    def _refresh_stats(self):
        for w in self.stats_outer.winfo_children(): w.destroy()
        mode = self.mode.get(); tbl = "factory_records" if mode=="factory" else "parlor_records"
        c.execute(f"SELECT COUNT(), AVG(day_sales), MAX(day_sales), MIN(day_sales) FROM {tbl}")
        row = c.fetchone(); cnt = row[0] or 0; avg_ds = row[1] or 0; max_ds = row[2] or 0; min_ds = row[3] or 0
        tk.Label(self.stats_outer, text="LIFETIME STATS", bg=BG2, fg=TEXT3, font=FONT_SECTION).pack(anchor="w", pady=(0,10))
        def sr(lbl, val, col=TEXT2):
            f = tk.Frame(self.stats_outer, bg=BG2); f.pack(fill="x", pady=4)
            tk.Label(f, text=lbl, bg=BG2, fg=TEXT3, font=FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=val, bg=BG2, fg=col, font=FONT_STAT).pack(anchor="w")
        sr("Total Entries", str(cnt), ACCENT_DIM)
        sr("Avg Day Sales", f"Rs {avg_ds:,.0f}", WARNING)
        sr("Max Day Sales", f"Rs {max_ds:,.0f}", SUCCESS)
        sr("Min Day Sales", f"Rs {min_ds:,.0f}", INFO)

    def _build_form_area(self):
        for w in self.left_col.winfo_children(): w.destroy()
        self.salary_widget = self.vehicle_widget = self.keb_widget = self.misc_widget = None
        mode = self.mode.get(); self.entries = {}
        inner = scrollable_frame(self.left_col, bg=SURFACE)
        pad = tk.Frame(inner, bg=SURFACE, padx=24, pady=18); pad.pack(fill="both", expand=True)
        tk.Label(pad, text=f"{'FACTORY' if mode=='factory' else 'PARLOUR'}  ENTRY FORM",
                 bg=SURFACE, fg=TEXT3, font=FONT_SECTION).pack(anchor="w", pady=(0,8))

        section_hdr(pad, "  DATE & BASIC INFO")
        dr = tk.Frame(pad, bg=SURFACE); dr.pack(fill="x", pady=3)
        dc = tk.Frame(dr, bg=SURFACE); dc.pack(side="left", fill="x", expand=True)
        tk.Label(dc, text="Date", bg=SURFACE, fg=TEXT3, font=FONT_LABEL).pack(anchor="w")
        df, e_date = styled_entry(dc, "DD-MM-YYYY"); df.pack(fill="x", pady=(2,0))
        e_date.delete(0,tk.END); e_date.insert(0, datetime.now().strftime("%d-%m-%Y")); e_date.config(fg=TEXT2)
        self.entries["date"] = e_date

        _, e_ob = form_row(pad, "Opening Balance (Rs)", "0.00", "\u2014", SURFACE)
        self.entries["opening_balance"] = e_ob
        e_ob.bind("<KeyRelease>", lambda e: self.update_net())

        section_hdr(pad, "  SALARY & ALLOWANCES")
        self.salary_widget = SalaryWidget(pad, bg=SURFACE, on_change=self.update_net)

        section_hdr(pad, "  VEHICLE EXPENSES")
        self.vehicle_widget = VehicleWidget(pad, bg=SURFACE, on_change=self.update_net)

        section_hdr(pad, "  MISCELLANEOUS EXPENSES")
        self.misc_widget = MiscWidget(pad, bg=SURFACE, on_change=self.update_net)

        section_hdr(pad, "  MILK EXPENSES")
        _, self.entries["milk_expenses"] = form_row(pad, "Milk Expense (Rs)", "0.00", "\u25cf", SURFACE)
        self.entries["milk_expenses"].bind("<KeyRelease>", lambda e: self.update_net())

        section_hdr(pad, "  KEB ELECTRICITY  (ADD YOUR METERS)")
        self.keb_widget = KEBWidget(pad, bg=SURFACE, on_change=self.update_net)

        section_hdr(pad, "  PURCHASES")
        _, self.entries["ice_cream_purchases"] = form_row(pad, "Ice Cream Purchases (Rs)", "0.00", "\u2014", SURFACE)
        self.entries["ice_cream_purchases"].bind("<KeyRelease>", lambda e: self.update_net())

        section_hdr(pad, "  PIGMY / SAVINGS")
        _, self.entries["pigmy"] = form_row(pad, "Pigmy Deposit (Rs)", "0.00", "\u25c8", SURFACE)
        self.entries["pigmy"].bind("<KeyRelease>", lambda e: self.update_net())

        tk.Frame(pad, bg=BORDER, height=1).pack(fill="x", pady=(16,12))
        br1 = tk.Frame(pad, bg=SURFACE); br1.pack(fill="x", pady=(0,6))
        make_button(br1, "  Save Record  ", self.save_record,
                    color=SURFACE3, hover=MUTED, fg=TEXT, padx=18, pady=10).pack(side="left", fill="x", expand=True, padx=(0,6))
        make_button(br1, "  Generate Report  ", self.generate_report,
                    color=SURFACE3, hover=MUTED, fg=TEXT, padx=18, pady=10).pack(side="left", fill="x", expand=True)
        br2 = tk.Frame(pad, bg=SURFACE); br2.pack(fill="x", pady=(0,4))
        make_button(br2, "  \U0001f4c8  View Trend  ",
                    lambda: show_trend(self.mode.get(), self.root),
                    color=SURFACE2, hover=SURFACE3, fg=INFO, padx=18, pady=9).pack(side="left", fill="x", expand=True, padx=(0,6))
        make_button(br2, "  View All Records  ",
                    lambda: view_all_records(self.mode.get(), self.root),
                    color=SURFACE2, hover=SURFACE3, fg=TEXT2, padx=18, pady=9).pack(side="left", fill="x", expand=True, padx=(0,6))
        make_button(br2, "  Reset  ", self.reset_fields,
                    color=SURFACE2, hover=SURFACE3, fg=TEXT3, padx=18, pady=9).pack(side="left")
        self.status_lbl = tk.Label(pad, textvariable=self.status_var,
                                   bg=SURFACE, fg=SUCCESS, font=("Consolas",9))
        self.status_lbl.pack(pady=(10,0), anchor="w")
        self.update_net()

    def _calculate(self):
        e = self.entries
        g = lambda k: get_float(e[k]) if k in e else 0.0
        ob = g("opening_balance"); milk = g("milk_expenses")
        sal  = self.salary_widget.get_total()         if self.salary_widget  else 0.0
        pet  = self.vehicle_widget.get_total_petrol() if self.vehicle_widget else 0.0
        vm   = self.vehicle_widget.get_total_maint()  if self.vehicle_widget else 0.0
        keb  = self.keb_widget.get_total()            if self.keb_widget     else 0.0
        misc = self.misc_widget.get_total()           if self.misc_widget    else 0.0
        icp  = g("ice_cream_purchases"); pig = g("pigmy")
        total_exp = sal + pet + vm + misc + keb + milk
        total_pur = icp
        total_out = ob + total_exp + total_pur + pig
        closing   = -total_exp - total_pur - pig
        day_sales = (total_exp + icp + pig) - ob
        return dict(total_salary=sal, total_vehicle=pet+vm,
                    total_misc=misc, total_keb=keb,
                    total_expenses=total_exp, total_purchases=total_pur,
                    total_outflow=total_out, closing_balance=closing,
                    day_sales=day_sales)

    def update_net(self):
        try:
            res = self._calculate(); ds = res["day_sales"]
            self.net_var.set(f"Rs {ds:,.2f}")
            is_pos = ds >= 0; bg = SUCCESS_BG if is_pos else DANGER_BG
            ds_col = WARNING if is_pos else DANGER
            for w in [self.net_card, self.net_inner, self.net_title,
                      self.net_label, self.net_sub, self.net_badge, self.breakdown_frame]:
                try: w.config(bg=bg)
                except: pass
            self.net_label.config(fg=ds_col)
            self.net_badge.config(text="\u25b2 POSITIVE" if is_pos else "\u25bc NEGATIVE", fg=ds_col)
            for w in self.breakdown_frame.winfo_children(): w.destroy()
            def mini(lbl, val, c2=TEXT3):
                f = tk.Frame(self.breakdown_frame, bg=bg); f.pack(fill="x", pady=1)
                tk.Label(f, text=lbl, bg=bg, fg=TEXT4, font=FONT_SMALL).pack(side="left")
                tk.Label(f, text=f"Rs{val:,.0f}", bg=bg, fg=c2, font=("Consolas", 8, "bold")).pack(side="right")
            mini("Salary",    res["total_salary"],    CH_SALARY)
            mini("Vehicle",   res["total_vehicle"],   CH_VEHICLE)
            mini("Misc",      res["total_misc"],      WARNING)
            mini("KEB",       res["total_keb"],       INFO)
            mini("Expenses",  res["total_expenses"],  DANGER)
            mini("Purchases", res["total_purchases"], INFO)
        except: self.net_var.set("Rs \u2014")

    def save_record(self):
        e = self.entries
        g = lambda k: get_float(e[k]) if k in e else 0.0
        date_v = e["date"].get().strip()
        if not date_v or date_v == "DD-MM-YYYY":
            messagebox.showerror("Missing", "Please enter the date.", parent=self.root); return

        mode = self.mode.get()
        if date_exists(date_v, mode):
            messagebox.showerror("Duplicate Date",
                f"A {mode} record for '{date_v}' already exists.\n"
                "Each date can only have one record. Use View All Records to edit it.",
                parent=self.root)
            return

        milk = g("milk_expenses"); res = self._calculate(); day_sales = res["day_sales"]
        keb_vals = self.keb_widget.get_all_values() if self.keb_widget else {}
        # For legacy columns: sum honnavar/ramthirth by name if present, else 0
        keb_hon = sum(v for k, v in keb_vals.items() if "Honnavar" in k)
        keb_ram = sum(v for k, v in keb_vals.items() if "Ramthirth" in k)
        icp = g("ice_cream_purchases"); pig = g("pigmy")
        tbl = "factory_records" if mode == "factory" else "parlor_records"

        c.execute(f"""INSERT INTO {tbl}
            (date, opening_balance, misc_expenses, ice_cream_purchases,
             keb_honnaver, keb_ramthirth, pigmy, milk_expenses, day_sales)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (date_v, g("opening_balance"),
             self.misc_widget.get_total() if self.misc_widget else 0,
             icp, keb_hon, keb_ram, pig, milk, day_sales))
        conn.commit()
        record_id = c.lastrowid

        if self.salary_widget:
            for emp_name, amt in self.salary_widget.get_entries():
                if amt > 0 or emp_name:
                    c.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                              (record_id, mode, emp_name, amt))
        if self.vehicle_widget:
            for vno, pet, maint in self.vehicle_widget.get_entries():
                c.execute("INSERT INTO vehicle_entries (record_id,record_type,vehicle_number,petrol,maintenance) VALUES (?,?,?,?,?)",
                          (record_id, mode, vno, pet, maint))
        if self.misc_widget:
            for purpose, amt in self.misc_widget.get_entries():
                if amt > 0 or purpose:
                    c.execute("INSERT INTO misc_entries (record_id,record_type,purpose,amount) VALUES (?,?,?,?)",
                              (record_id, mode, purpose, amt))
        if self.keb_widget:
            for meter, amt in keb_vals.items():
                if amt > 0:
                    c.execute("INSERT INTO keb_entries (record_id,record_type,meter_name,amount) VALUES (?,?,?,?)",
                              (record_id, mode, meter, amt))
        conn.commit()
        self.status_var.set(f"  \u2713  Saved!  Day Sales = Rs {day_sales:,.2f}")
        self.status_lbl.config(fg=SUCCESS)
        self.root.after(4000, lambda: self.status_var.set(""))
        self._refresh_stats(); self.reset_fields()

    def generate_report(self):
        e = self.entries; g = lambda k: get_float(e[k]) if k in e else 0.0
        mode = self.mode.get()
        data = {
            "date": e["date"].get().strip() or datetime.now().strftime("%d-%m-%Y"),
            "opening_balance":     g("opening_balance"),
            "salary_entries":      self.salary_widget.get_entries()  if self.salary_widget  else [],
            "vehicle_entries":     self.vehicle_widget.get_entries() if self.vehicle_widget else [],
            "misc_entries":        self.misc_widget.get_entries()    if self.misc_widget    else [],
            "keb_values":          self.keb_widget.get_all_values()  if self.keb_widget     else {},
            "milk_expenses":       g("milk_expenses"),
            "ice_cream_purchases": g("ice_cream_purchases"),
            "pigmy":               g("pigmy"),
        }
        show_report(mode, data, self._calculate(), self.root)

    def reset_fields(self):
        for key, ent in self.entries.items():
            if key == "date":
                ent.delete(0, tk.END); ent.insert(0, datetime.now().strftime("%d-%m-%Y")); ent.config(fg=TEXT2)
            else:
                ent.delete(0, tk.END); ent.insert(0, "0.00"); ent.config(fg=TEXT3)
        if self.salary_widget:  self.salary_widget.reset()
        if self.vehicle_widget: self.vehicle_widget.reset()
        if self.keb_widget:     self.keb_widget.reset()
        if self.misc_widget:    self.misc_widget.reset()
        self.update_net()

    def switch_mode(self):
        mode = self.mode.get(); acc = FACTORY_AC if mode == "factory" else ACCENT
        self.title_lbl.config(text=f"KARAVALI {'ICE CREAM FACTORY' if mode=='factory' else 'ICE CREAM PARLOUR'}")
        self.sub_lbl.config(text=f"Daily Financial Management System  \u00b7  {'Factory' if mode=='factory' else 'Parlour'} Mode")
        self.accent_bar.config(bg=acc); self.accent_line.config(bg=acc)
        self._build_form_area(); self._refresh_stats()

    def _build_footer(self):
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")
        foot = tk.Frame(self.root, bg=SURFACE, pady=7); foot.pack(fill="x")
        tk.Frame(foot, bg=MUTED, width=4).pack(side="left", fill="y")
        tk.Label(foot, text="  KARAVALI ICE CREAM   \u00b7   Financial Management System   \u00b7   ",
                 bg=SURFACE, fg=TEXT4, font=FONT_BRAND).pack(side="left", padx=12)
        tk.Label(foot, text=f"DB: {db_path()}  ",
                 bg=SURFACE, fg=TEXT4, font=FONT_BRAND).pack(side="right", padx=12)


root = tk.Tk()
app  = KaravaliApp(root)
try:
    icon = tk.PhotoImage(file=resource_path("icon.png"))
    root.iconphoto(True, icon)
except Exception:
    pass

root.mainloop()
conn.close()