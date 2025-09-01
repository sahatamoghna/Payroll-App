import tkinter as tk
from db_manager import init_db
import login_screen

def main():
    # Ensure database exists
    init_db()

    # Create a single root window
    root = tk.Tk()
    root.title("Payroll App")
    root.geometry("950x650")
    root.resizable(False, False)

    # Start on the login “screen”
    login_screen.show_login(root)

    # Enter the mainloop
    root.mainloop()

if __name__ == "__main__":
    main()
