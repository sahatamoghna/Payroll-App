import os
import sys
import subprocess
import shutil
import calendar
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import show_error, show_info, get_reports_folder_path
from db_manager import fetch_payslips, delete_payslip

def open_file(path):
    if sys.platform.startswith('darwin'):
        subprocess.call(['open', path])
    elif os.name == 'nt':
        os.startfile(path)
    else:
        subprocess.call(['xdg-open', path])

def render(parent):
    for w in parent.winfo_children():
        w.destroy()
    style = ttk.Style(parent)
    style.theme_use('clam')
    style.configure('Content.TFrame', background='#FFFFFF')
    style.configure('Treeview',
                    font=('Segoe UI', 12),
                    rowheight=28,
                    background='#FFFFFF',
                    fieldbackground='#FFFFFF',
                    foreground='#333333')
    style.configure('Treeview.Heading',
                    font=('Segoe UI', 13, 'bold'),
                    background='#F0F0F0',
                    foreground='#333333')
    style.configure('Action.TButton',
                    font=('Segoe UI', 12, 'bold'),
                    background='#6BBF44',
                    foreground='white',
                    padding=(6, 4))
    style.map('Action.TButton',
              background=[('active', '#57A738')])

    # Container
    frame = ttk.Frame(parent, style='Content.TFrame', padding=20)
    frame.pack(fill='both', expand=True)

    # Treeview with checkbox column
    cols = ("Select", "Staff ID", "Month", "Year", "Filename", "Timestamp")
    tree = ttk.Treeview(frame,
                        columns=cols,
                        show='headings',
                        selectmode='none')
    tree.pack(fill='both', expand=True, pady=(0,10))

    # Headings & alignment
    for col in cols:
        heading = "" if col == "Select" else col
        tree.heading(col, text=heading)
        # default to center except Filename
        anchor = 'w' if col == 'Filename' else 'center'
        tree.column(col, anchor=anchor, stretch=True)

    # Track checkbox state
    selected = {}

    # Populate rows
    for ps_id, staff_id, month, year, filename, timestamp in fetch_payslips():
        mon_abbr = calendar.month_abbr[int(month)]
        selected[str(ps_id)] = False
        tree.insert('', 'end', iid=str(ps_id),
                    values=("☐", staff_id, mon_abbr, year, filename, timestamp))

    # Auto-size columns to fill width 
    # proportions sum to 1.0
    widths = {
        "Select":   0.06,
        "Staff ID": 0.12,
        "Month":    0.10,
        "Year":     0.10,
        "Filename": 0.42,
        "Timestamp":0.20
    }
    def autosize(event):
        total = tree.winfo_width()
        if total <= 0:
            return
        for col, frac in widths.items():
            tree.column(col, width=int(total * frac))
    tree.bind('<Configure>', autosize)

    # Toggle checkbox on click 
    def on_click(event):
        region = tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = tree.identify_column(event.x)
        if col != "#1":
            return
        row = tree.identify_row(event.y)
        if not row:
            return
        sel = not selected[row]
        selected[row] = sel
        tree.set(row, "Select", "☑" if sel else "☐")
        return "break"
    tree.bind('<Button-1>', on_click)

    # Button bar 
    btn_frame = ttk.Frame(frame, style='Content.TFrame')
    btn_frame.pack(fill='x')

    def get_selected_ids():
        return [rid for rid, v in selected.items() if v]

    def on_open():
        ids = get_selected_ids()
        if len(ids) != 1:
            show_error("Please select exactly one payslip to open.")
            return
        fn = tree.item(ids[0], 'values')[4]
        open_file(os.path.join(get_reports_folder_path(), fn))

    def on_download():
        ids = get_selected_ids()
        if not ids:
            show_error("Select at least one payslip to download.")
            return
        dest = filedialog.askdirectory(title="Select download folder")
        if not dest:
            return
        for rid in ids:
            fn = tree.item(rid, 'values')[4]
            src = os.path.join(get_reports_folder_path(), fn)
            try:
                shutil.copy(src, dest)
            except Exception as e:
                show_error(f"Failed to copy {fn}:\n{e}")
        show_info(f"Downloaded {len(ids)} payslip(s) to:\n{dest}")

    def on_delete():
        ids = get_selected_ids()
        if not ids:
            show_error("Select at least one payslip to delete.")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete {len(ids)} payslip(s)?"):
            return
        for rid in ids:
            fn = delete_payslip(int(rid))
            if fn:
                path = os.path.join(get_reports_folder_path(), fn)
                try:
                    os.remove(path)
                except FileNotFoundError:
                    pass
                tree.delete(rid)
                selected.pop(rid, None)
        show_info(f"Deleted {len(ids)} payslip(s).")

    ttk.Button(btn_frame, text="Open",     style='Action.TButton', command=on_open)   .pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Download", style='Action.TButton', command=on_download).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Delete",   style='Action.TButton', command=on_delete)  .pack(side='left', padx=5)
