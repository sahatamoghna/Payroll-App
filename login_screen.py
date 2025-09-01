# login_screen.py

import os, sys, tkinter as tk
from tkinter import ttk
from utils import USERNAME, PASSWORD, ICON_PATH, show_error, RESOURCE_DIR
import main_menu

def show_login(root):
    # Clear previous widgets & background 
    for w in root.winfo_children():
        w.destroy()
    root.configure(bg='#f4f4f4')

    # Load logo from RESOURCE_DIR
    logo_path = os.path.join(RESOURCE_DIR, 'assets', 'logo.png')
    try:
        orig = tk.PhotoImage(file=logo_path)
        logo_img = orig.subsample(2, 2)
    except Exception:
        logo_img = None

    # Style setup 
    style = ttk.Style(root)
    style.theme_use('clam')

    style.configure('Login.TFrame', background='#f4f4f4')
    style.configure('Login.TLabel', background='#f4f4f4', font=('Segoe UI', 16))
    style.configure('Login.TEntry',
                    font=('Segoe UI', 16),
                    padding=6,
                    fieldbackground='white')
    style.configure('Login.TButton',
                    font=('Segoe UI', 14, 'bold'),
                    foreground='white',
                    background='#6BBF44',
                    padding=6)
    style.map('Login.TButton',
              background=[('active', '#8DDB6E')])

    if logo_img:
        logo_frame = ttk.Frame(root, style='Login.TFrame')
        logo_frame.place(relx=0.5, rely=0.1, anchor='center')  # top-center
        logo_label = ttk.Label(logo_frame, image=logo_img, style='Login.TLabel')
        logo_label.image = logo_img
        logo_label.pack()

    # Login Form Centered 
    form = ttk.Frame(root, style='Login.TFrame', padding=(20, 20))
    form.place(relx=0.5, rely=0.5, anchor='center')

    user_var = tk.StringVar()
    pwd_var  = tk.StringVar()

    ttk.Label(form, text="Username:", style='Login.TLabel')\
        .grid(row=0, column=0, sticky='e', pady=8, padx=(0,10))
    user_entry = ttk.Entry(form, textvariable=user_var, style='Login.TEntry', width=22)
    user_entry.grid(row=0, column=1, pady=8)

    ttk.Label(form, text="Password:", style='Login.TLabel')\
        .grid(row=1, column=0, sticky='e', pady=8, padx=(0,10))
    pwd_entry = ttk.Entry(form, textvariable=pwd_var, show='*', style='Login.TEntry', width=22)
    pwd_entry.grid(row=1, column=1, pady=8)

    def attempt_login(event=None):
        if user_var.get().strip() == USERNAME and pwd_var.get().strip() == PASSWORD:
            main_menu.show_main_app(root)
        else:
            show_error("Invalid username or password.", title="Login Failed")

    login_btn = ttk.Button(form, text="Login", style='Login.TButton', command=attempt_login)
    login_btn.grid(row=2, column=0, columnspan=2, pady=(25,0), sticky='ew')

    user_entry.focus_set()
    root.bind('<Return>', attempt_login)
