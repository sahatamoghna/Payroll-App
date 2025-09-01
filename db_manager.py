import sqlite3
from utils import get_db_path

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    # Reports & Payslips 
    c.execute("""
      CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        filename TEXT NOT NULL,
        timestamp TEXT NOT NULL
      )
    """)
    c.execute("""
      CREATE TABLE IF NOT EXISTS payslips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id TEXT NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        filename TEXT NOT NULL,
        timestamp TEXT NOT NULL
      )
    """)

    # Tax slabs + backup defaults
    c.execute("""
      CREATE TABLE IF NOT EXISTS tax_slabs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lower_bound REAL NOT NULL,
        upper_bound REAL,
        rate REAL NOT NULL
      )
    """)
    c.execute("""
      CREATE TABLE IF NOT EXISTS default_tax_slabs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lower_bound REAL NOT NULL,
        upper_bound REAL,
        rate REAL NOT NULL
      )
    """)

    # Seed original seven‐bracket defaults if table is empty
    c.execute("SELECT COUNT(*) FROM tax_slabs")
    if c.fetchone()[0] == 0:
        originals = [
            (0,        490,       0),
            (490,      600,       5),
            (600,      730,      10),
            (730,    3896.67,   17.5),
            (3896.67,19896.67,   25),
            (19896.67,50000,     30),
            (50000,   None,      35),
        ]
        for lo, up, rt in originals:
            c.execute(
                "INSERT INTO tax_slabs (lower_bound, upper_bound, rate) VALUES (?,?,?)",
                (lo, up, rt)
            )

    # Mirror into default_tax_slabs if that table is empty
    c.execute("SELECT COUNT(*) FROM default_tax_slabs")
    if c.fetchone()[0] == 0:
        c.execute("""
          INSERT INTO default_tax_slabs (lower_bound, upper_bound, rate)
          SELECT lower_bound, upper_bound, rate FROM tax_slabs
        """)

    conn.commit()
    conn.close()

# Report CRUD 
def insert_report(month: int, year: int, filename: str, timestamp: str) -> int:
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute(
        "INSERT INTO reports (month, year, filename, timestamp) VALUES (?,?,?,?)",
        (month, year, filename, timestamp)
    )
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return rid

def fetch_reports() -> list:
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute(
        "SELECT id, month, year, filename, timestamp "
        "FROM reports ORDER BY year DESC, month DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows

def delete_report(report_id: int) -> str:
    """
    Remove the report record and return its filename (so caller can delete the file).
    """
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("SELECT filename FROM reports WHERE id = ?", (report_id,))
    row = c.fetchone()
    if row:
        fn = row[0]
        c.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
    else:
        fn = None
    conn.close()
    return fn

# Payslip CRUD
def insert_payslip(staff_id, month, year, filename, timestamp):
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute(
      "INSERT INTO payslips (staff_id, month, year, filename, timestamp) VALUES (?,?,?,?,?)",
      (staff_id, month, year, filename, timestamp)
    )
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid

def fetch_payslips():
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute(
        "SELECT id, staff_id, month, year, filename, timestamp "
        "FROM payslips ORDER BY year DESC, month DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows

def delete_payslip(ps_id):
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("SELECT filename FROM payslips WHERE id = ?", (ps_id,))
    row = c.fetchone()
    if row:
        fn = row[0]
        c.execute("DELETE FROM payslips WHERE id = ?", (ps_id,))
        conn.commit()
    else:
        fn = None
    conn.close()
    return fn

# Tax Slab CRUD / Defaults
def fetch_tax_slabs():
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("SELECT id, lower_bound, upper_bound, rate FROM tax_slabs ORDER BY lower_bound")
    rows = c.fetchall()
    conn.close()
    return [{'id':r[0],'lower':r[1],'upper':r[2],'rate':r[3]} for r in rows]

def clear_tax_slabs():
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("DELETE FROM tax_slabs")
    conn.commit(); conn.close()

def reset_tax_slabs():
    """
    Restore the ORIGINAL seven‐bracket defaults from default_tax_slabs.
    """
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("DELETE FROM tax_slabs")
    c.execute("""
      INSERT INTO tax_slabs(lower_bound, upper_bound, rate)
      SELECT lower_bound, upper_bound, rate FROM default_tax_slabs
    """)
    conn.commit(); conn.close()

def set_default_tax_slabs():
    """
    Overwrite default_tax_slabs with the current tax_slabs.
    """
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("DELETE FROM default_tax_slabs")
    c.execute("""
      INSERT INTO default_tax_slabs(lower_bound, upper_bound, rate)
      SELECT lower_bound, upper_bound, rate FROM tax_slabs
    """)
    conn.commit(); conn.close()

def add_tax_slab(lower, upper, rate):
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("INSERT INTO tax_slabs(lower_bound, upper_bound, rate) VALUES (?,?,?)",
              (lower, upper, rate))
    conn.commit(); conn.close()

def delete_tax_slab(slab_id):
    conn = sqlite3.connect(get_db_path()); c = conn.cursor()
    c.execute("DELETE FROM tax_slabs WHERE id=?", (slab_id,))
    conn.commit(); conn.close()
