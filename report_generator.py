# report_generator.py

import os
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import pandas as pd

from utils import show_error, show_info, format_timestamp, get_reports_folder_path
from db_manager import (
    init_db, fetch_reports, insert_report,
    fetch_tax_slabs, clear_tax_slabs, reset_tax_slabs, add_tax_slab
)
from excel_utils import generate_payroll_report

# ─── Simple UI state cache ────────────────────────────────────────────────────
_rg_state = {
    'path': '',
    'month': '',
    'year': ''
}

def render(parent):
    init_db()
    root = parent.winfo_toplevel()
    root.geometry("950x650")
    root.resizable(True, True)

    # ─── Styles ───────────────────────────────────────────────────────────────
    style = ttk.Style(parent)
    style.theme_use('clam')
    style.configure('Content.TFrame', background='#FFFFFF')
    style.configure('Content.TLabel', background='#FFFFFF', font=('Segoe UI',12))
    style.configure('Content.TEntry', font=('Segoe UI',12), padding=5)
    style.configure('Content.TCombobox',
                    font=('Segoe UI',12),
                    fieldbackground='#FFFFFF', background='#FFFFFF',
                    foreground='#333333', arrowsize=15, padding=2)
    style.map('Content.TCombobox',
              fieldbackground=[('readonly','#FFFFFF')],
              background=[('readonly','#FFFFFF')],
              foreground=[('readonly','#333333')])
    style.configure('Action.TButton',
                    font=('Segoe UI',12,'bold'),
                    background='#6BBF44', foreground='white',
                    padding=(6,4))
    style.map('Action.TButton', background=[('active','#57A738')])

    # ─── Main container ───────────────────────────────────────────────────────
    container = ttk.Frame(parent, style='Content.TFrame', padding=10)
    container.pack(fill='both', expand=True)
    container.columnconfigure(0, weight=1)

    # ─── Top row: Input + Browse + Edit Slabs ────────────────────────────────
    top = ttk.Frame(container, style='Content.TFrame')
    top.grid(row=0, column=0, sticky='nw', padx=10, pady=5)

    # File path var + trace
    path_var = tk.StringVar(value=_rg_state['path'])
    def _on_path_change(*_):
        _rg_state['path'] = path_var.get()
        load_preview()
    path_var.trace_add('write', _on_path_change)

    ttk.Label(top, text="Input Excel:", style='Content.TLabel')\
        .grid(row=0, column=0, sticky='e', padx=2, pady=2)
    ttk.Entry(top, textvariable=path_var, style='Content.TEntry', width=30)\
        .grid(row=0, column=1, sticky='w', padx=2, pady=2)
    ttk.Button(top, text="Browse", style='Action.TButton',
               command=lambda: path_var.set(
                   filedialog.askopenfilename(
                       title="Select Excel",
                       filetypes=[("Excel","*.xlsx *.xls")]
                   )
               )).grid(row=0, column=2, padx=2, pady=2)
    ttk.Button(top, text="Edit PAYE Slabs", style='Action.TButton',
               command=lambda: open_slab_editor(parent))\
        .grid(row=0, column=3, padx=2, pady=2)

    # ─── Date selection ───────────────────────────────────────────────────────
    months = [datetime.date(2000, m, 1).strftime('%B') for m in range(1,13)]
    years  = [str(y) for y in range(2025, datetime.datetime.now().year+6)]

    date_frame = ttk.Frame(top, style='Content.TFrame')
    date_frame.grid(row=1, column=1, columnspan=3, sticky='w', padx=2, pady=15)

    ttk.Label(date_frame, text="Month:", style='Content.TLabel')\
        .pack(side='left', padx=(0,5))
    month_cb = ttk.Combobox(date_frame,
                            values=months,
                            state='readonly',
                            style='Content.TCombobox',
                            width=12)
    month_cb.pack(side='left')
    if _rg_state['month']:
        month_cb.set(_rg_state['month'])
    month_cb.bind("<<ComboboxSelected>>",
                  lambda e: _rg_state.update(month=month_cb.get()))

    ttk.Label(date_frame, text="Year:", style='Content.TLabel')\
        .pack(side='left', padx=(15,5))
    year_cb = ttk.Combobox(date_frame,
                           values=years,
                           state='readonly',
                           style='Content.TCombobox',
                           width=8)
    year_cb.pack(side='left')
    if _rg_state['year']:
        year_cb.set(_rg_state['year'])
    year_cb.bind("<<ComboboxSelected>>",
                 lambda e: _rg_state.update(year=year_cb.get()))

    # ─── Preview ──────────────────────────────────────────────────────────────
    ttk.Label(container, text="Preview", style='Content.TLabel')\
        .grid(row=2, column=0, sticky='w', padx=10, pady=(10,0))
    preview_frame = ttk.Frame(container, style='Content.TFrame')
    preview_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
    container.rowconfigure(3, weight=1)

    preview = ttk.Treeview(preview_frame, show='headings')
    preview.pack(fill='both', expand=True)

    # Buttons for Save / Discard
    btn_frame = ttk.Frame(preview_frame)
    btn_frame.pack(fill='x', anchor='e')
    save_input_btn = ttk.Button(btn_frame, text="Save Input Changes",
                                style='Action.TButton')
    discard_input_btn = ttk.Button(btn_frame, text="Discard Changes",
                                   style='Action.TButton')
    save_input_btn.pack_forget()
    discard_input_btn.pack_forget()

    # ─── Data & expected header ──────────────────────────────────────────────
    preview_df = {'df': None, 'orig': None}
    expected_cols = [
        'Name',
        'STAFF ID',
        'Social Security No.',
        'Tin No.',
        'POSITION',
        'Basic Salary',
        'Allowances',
        'OT',
        'Loan Repayment'
    ]

    def load_preview(*_):
        p = _rg_state['path']
        if not p.endswith(('.xls','.xlsx')):
            return
        try:
            df = pd.read_excel(p, dtype={
                'Social Security No.': str,
                'Tin No.': str
            })
        except Exception as e:
            show_error(f"Preview failed:\n{e}")
            return

        # Replace NaN in numeric columns with 0
        for col in ['Basic Salary', 'Allowances', 'OT', 'Loan Repayment']:
            if col in df.columns:
                df[col].fillna(0, inplace=True)

        # header check
        if list(df.columns) != expected_cols:
            show_error(
                "Invalid Excel format.\n"
                "Expected columns (in order):\n"
                f"{', '.join(expected_cols)}",
                title="Wrong Format"
            )
            return

        preview_df['orig'] = df.copy()
        preview_df['df']   = df.copy()

        preview.delete(*preview.get_children())
        preview['columns'] = expected_cols
        for c in expected_cols:
            preview.heading(c, text=c, anchor='center')
            preview.column(c, width=100, anchor='center')
        for i, row in enumerate(df.itertuples(index=False)):
            preview.insert('', 'end', iid=str(i), values=tuple(row))

        save_input_btn.pack_forget()
        discard_input_btn.pack_forget()

    # automatically reload if path already set
    load_preview()

    def on_preview_double(e):
        if preview.identify("region", e.x, e.y) != "cell":
            return
        col = preview.identify_column(e.x)
        row = preview.identify_row(e.y)
        if not row:
            return
        x,y,w,h = preview.bbox(row, col)
        ci = int(col.replace('#','')) - 1
        old = preview.set(row, col)
        editor = ttk.Entry(preview)
        editor.place(x=x, y=y, width=w, height=h)
        editor.insert(0, old)
        editor.focus()

        def save_(ev=None):
            new = editor.get()
            preview.set(row, col, new)
            df = preview_df['df']
            df.iat[int(row), ci] = new
            editor.destroy()
            save_input_btn.pack(side='left', padx=(0,5), pady=(5,0))
            discard_input_btn.pack(side='left', pady=(5,0))

        editor.bind("<Return>", save_)
        editor.bind("<FocusOut>", save_)

    preview.bind("<Double-1>", on_preview_double)

    def on_save():
        df = preview_df['df']
        try:
            df.to_excel(_rg_state['path'], index=False)
            show_info("Input file updated", title="Saved")
            load_preview()
        except Exception as e:
            show_error(f"Could not save input:\n{e}")

    def on_discard():
        orig = preview_df['orig']
        if orig is None:
            return
        try:
            orig.to_excel(_rg_state['path'], index=False)
            show_info("Changes discarded", title="Discard")
            load_preview()
        except Exception as e:
            show_error(f"Could not discard changes:\n{e}")

    save_input_btn.config(command=on_save)
    discard_input_btn.config(command=on_discard)

    # ─── Bottom: Apply Slabs & Generate ───────────────────────────────────────
    def on_generate():
        p = _rg_state['path']
        if not p.endswith(('.xls','.xlsx')):
            show_error("Select a valid Excel"); return

        # header check
        try:
            df_check = pd.read_excel(p, dtype={
                'Social Security No.': str,
                'Tin No.': str
            }, nrows=0)
        except Exception as e:
            show_error(f"Failed reading Excel:\n{e}"); return
        if list(df_check.columns) != expected_cols:
            show_error(
                "Invalid Excel format.\n"
                "Expected columns (in order):\n"
                f"{', '.join(expected_cols)}",
                title="Wrong Format"
            )
            return

        try:
            m = months.index(_rg_state['month']) + 1
            y = int(_rg_state['year'])
        except:
            show_error("Select month & year"); return

        if any(r[1] == m and r[2] == y for r in fetch_reports()):
            show_error("Report exists—delete first"); return

        slabs = fetch_tax_slabs()
        try:
            out = generate_payroll_report(p, m, y, slabs=slabs)
            insert_report(m, y, os.path.basename(out), format_timestamp())
            show_info(f"Report saved:\n{out}")

            # ─── CLEAR everything after success ─────────────────────────────
            path_var.set('')
            _rg_state.update(path='', month='', year='')
            month_cb.set('')
            year_cb.set('')
            preview.delete(*preview.get_children())
            preview['columns'] = []
            preview_df['df'] = preview_df['orig'] = None
            save_input_btn.pack_forget()
            discard_input_btn.pack_forget()

        except Exception as e:
            show_error(f"Failed:\n{e}")

    ttk.Button(container, text="Apply Slabs & Generate",
               style='Action.TButton', command=on_generate)\
       .grid(row=4, column=0, pady=10)


def open_slab_editor(parent):
    # ─── Create & center pop-up ───────────────────────────────────────────────
    win = tk.Toplevel(parent)
    win.title("Edit PAYE Slabs")
    w, h = 400, 400
    root = parent.winfo_toplevel()
    root.update_idletasks()
    rx, ry = root.winfo_x(), root.winfo_y()
    rw, rh = root.winfo_width(), root.winfo_height()
    x = rx + (rw - w)//2
    y = ry + (rh - h)//2
    win.geometry(f"{w}x{h}+{x}+{y}")
    win.transient(root); win.grab_set()

    # ─── Styles & Container ───────────────────────────────────────────────────
    style = ttk.Style(win)
    style.theme_use('clam')
    frame = ttk.Frame(win, style='Content.TFrame', padding=10)
    frame.pack(fill='both', expand=True)

    style.configure('Treeview',
                    background='#FFFFFF', fieldbackground='#FFFFFF',
                    foreground='#333333', rowheight=20)
    style.configure('Treeview.Heading', font=('Segoe UI',10,'bold'))
    style.configure('Action.TButton',
                    font=('Segoe UI',12,'bold'),
                    background='#6BBF44', foreground='white', padding=(6,4))
    style.map('Action.TButton', background=[('active','#57A738')])

    # ─── Load & Edit Slabs ────────────────────────────────────────────────────
    slabs = fetch_tax_slabs()

    cols = ("From","To","Rate","")
    tree = ttk.Treeview(frame, columns=cols, show='headings', height=8)
    for c, wid in zip(cols, (100,100,80,30)):
        tree.heading(c, text=c)
        tree.column(c, width=wid, anchor='center')
    tree.pack(fill='both', expand=True)

    def load():
        tree.delete(*tree.get_children())
        for i, s in enumerate(slabs):
            to_txt = "" if s['upper'] is None else str(s['upper'])
            tree.insert('', 'end', iid=str(i),
                        values=(s['lower'], to_txt, f"{s['rate']}%", "❌"))
        tree.insert('', 'end', iid='__add__',
                    values=('','','','➕'))
    load()

    def on_click(e):
        col = tree.identify_column(e.x)
        row = tree.identify_row(e.y)
        if col != '#4' or not row:
            return

        if row == '__add__':
            # Rule #2: only one open-ended slab allowed
            if any(s['upper'] is None for s in slabs):
                show_error("You can only have one slab with a blank 'To'.", title="Cannot Add")
                return

            lo = simpledialog.askfloat("From GHS", "Enter lower bound:", parent=win)
            if lo is None: return
            rt = simpledialog.askfloat("Rate %", "Enter rate (%):", parent=win)
            if rt is None: return
            up_str = simpledialog.askstring("To GHS", "Enter upper bound (blank=∞):", parent=win)

            slabs.append({
                'lower': lo,
                'upper': None if not up_str else float(up_str),
                'rate':  rt
            })
        else:
            slabs.pop(int(row))

        load()

    tree.bind("<Button-1>", on_click)

    def on_double(e):
        if tree.identify("region", e.x, e.y) != "cell": return
        col, row = tree.identify_column(e.x), tree.identify_row(e.y)
        if row == '__add__': return
        x, y, wid, ht = tree.bbox(row, col)
        ci = int(col.replace('#','')) - 1
        old = tree.set(row, col)
        if ci == 2 and old.endswith('%'):
            old = old[:-1]
        editor = ttk.Entry(tree)
        editor.place(x=x, y=y, width=wid, height=ht)
        editor.insert(0, old)
        editor.focus()

        def save_(ev=None):
            val = editor.get()
            if ci == 0:
                slabs[int(row)]['lower'] = float(val)
            elif ci == 1:
                slabs[int(row)]['upper'] = None if val == '' else float(val)
            else:
                slabs[int(row)]['rate'] = float(val)
            editor.destroy()
            load()

        editor.bind("<Return>", save_)
        editor.bind("<FocusOut>", save_)

    tree.bind("<Double-1>", on_double)

    def on_save():
        # Rule #1: final slab must have blank To
        if not slabs or slabs[-1]['upper'] is not None:
            show_error("Final slab must have blank 'To' to cover ∞.", title="Invalid Slabs")
            return
        # Rule #3: each lower must equal previous upper
        for i in range(1, len(slabs)):
            prev, curr = slabs[i-1], slabs[i]
            if curr['lower'] != prev['upper']:
                show_error(
                    f"Row {i+1} From ({curr['lower']})\n"
                    f"does not match previous To ({prev['upper']}).",
                    title="Invalid Slabs"
                )
                return
        # Persist
        clear_tax_slabs()
        for s in slabs:
            add_tax_slab(s['lower'], s['upper'], s['rate'])
        win.destroy()
        show_info("Slabs updated successfully", title="Done")

    # Buttons: Reset, Cancel, Save
    btns = ttk.Frame(frame)
    btns.pack(pady=10)
    ttk.Button(btns, text="Reset", style='Action.TButton',
               command=lambda: [
                   reset_tax_slabs(),
                   slabs.clear(),
                   slabs.extend(fetch_tax_slabs()),
                   load()
               ]).pack(side='left', padx=5)
    ttk.Button(btns, text="Cancel", style='Action.TButton',
               command=win.destroy).pack(side='left', padx=5)
    ttk.Button(btns, text="Save", style='Action.TButton',
               command=on_save).pack(side='left', padx=5)
