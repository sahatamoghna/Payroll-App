import tkinter as tk
from tkinter import ttk
from utils import ICON_PATH
import report_generator
import view_reports
import payslip_generator
import view_payslips

def show_main_app(root):
    for w in root.winfo_children():
        w.destroy()

    # Apply window icon 
    if ICON_PATH:
        try:
            root.iconbitmap(ICON_PATH)
        except Exception:
            pass

    # Styles
    style = ttk.Style(root)
    style.theme_use('clam')

    # Navigation frame (left)
    style.configure('Nav.TFrame', background='#F9F9F9')
    style.configure('Nav.TButton',
                    background='#F9F9F9',
                    foreground='#333333',
                    font=('Segoe UI', 14),
                    borderwidth=0,
                    anchor='w',
                    padding=(20, 10))
    style.map('Nav.TButton',
              background=[('active', '#E0E0E0')])

    style.configure('NavActive.TButton',
                    background='#6BBF44',
                    foreground='white',
                    font=('Segoe UI', 14, 'bold'),
                    borderwidth=0,
                    anchor='w',
                    padding=(20, 10))
    style.map('NavActive.TButton',
              background=[('active', '#57A738')])

    # Content frame
    style.configure('Content.TFrame', background='#FFFFFF')

    # Layout
    nav_frame = ttk.Frame(root, style='Nav.TFrame', width=250)
    nav_frame.pack(side='left', fill='y')
    nav_frame.pack_propagate(False)

    sep = ttk.Separator(root, orient='vertical')
    sep.pack(side='left', fill='y')

    content_frame = ttk.Frame(root, style='Content.TFrame')
    content_frame.pack(side='left', fill='both', expand=True)

    # Nav Buttons
    btn_generate = ttk.Button(nav_frame,
                              text="Generate Report",
                              style='Nav.TButton',
                              command=lambda: on_nav('generate'))
    btn_generate.pack(fill='x', pady=(20,1))

    btn_view = ttk.Button(nav_frame,
                          text="View Reports",
                          style='Nav.TButton',
                          command=lambda: on_nav('view'))
    btn_view.pack(fill='x', pady=1)

    btn_payslip = ttk.Button(nav_frame,
                             text="Payslips",
                             style='Nav.TButton',
                             command=lambda: on_nav('payslip'))
    btn_payslip.pack(fill='x', pady=1)

    # Navigation logic
    def on_nav(section):
        # Reset all buttons to inactive style
        btn_generate.configure(style='Nav.TButton')
        btn_view.configure(style='Nav.TButton')
        btn_payslip.configure(style='Nav.TButton')

        # Clear content frame
        for w in content_frame.winfo_children():
            w.destroy()

        # Activate the selected section
        if section == 'generate':
            btn_generate.configure(style='NavActive.TButton')
            report_generator.render(content_frame)

        elif section == 'view':
            btn_view.configure(style='NavActive.TButton')
            view_reports.render(content_frame)

        elif section == 'payslip':
            btn_payslip.configure(style='NavActive.TButton')
            payslip_generator.render(content_frame)

    # Default landing page 
    on_nav('generate')
