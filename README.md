# Payroll App

A desktop **Payroll Management Tool** built with Tkinter to generate monthly Payroll Reports and individual Payslips from Excel staff data.  
The app supports configurable PAYE tax slabs, SSF/Tier calculations, and stores metadata in a lightweight SQLite database.

---

## ✨ Features

- **Payroll Report Generation**  
  - Import staff details from Excel (using a bundled template)  
  - Apply PAYE slabs, SSF, and employer contributions  
  - Save monthly payroll reports, tracked in the database  

- **Payslip Generation**  
  - Create individual PDF payslips for each staff member  
  - Custom date field printed on payslips  
  - Outputs organized under a chosen destination folder  

- **PAYE Slab Editor**  
  - Add, update, or remove tax slabs directly in the GUI  
  - Enforce rules (one open-ended slab, ranges must connect)  
  - Reset to default 7-bracket structure at any time  

- **Report & Payslip Management**  
  - View, open, copy, or delete past reports/payslips from within the app  

- **Authentication**  
  - Simple login screen with credentials stored in `config.ini` (default: `admin` / `password123`)  

- **Portability**  
  - Uses SQLite for persistence  
  - App data folders created automatically  
  - Packaged into a standalone `.exe` with PyInstaller  

---

## 🛠️ Tech Stack

- Python 3.10+  
- Tkinter (GUI)  
- pandas, openpyxl (Excel handling)  
- reportlab, PyPDF2 (PDF generation)  
- sqlite3 (database)  
- PyInstaller (packaging)  

---

## 🚀 Running the App (Development)

```bash
python main.py
````

* On first launch, the app initializes the SQLite database and opens the **Login** screen.
* Default credentials:

  * Username: `admin`
  * Password: `password123`

---

## 📑 Input Excel Format

The payroll generator expects the following columns in the header row (case & order must match):

```
Name | STAFF ID | Social Security No. | Tin No. | POSITION | Basic Salary | Allowances | OT | Loan Repayment
```

---

## 📊 Payroll Computations

* **Gross Salary** = Basic Salary + Allowances + OT
* **SSF (Employee)** = Basic × (rate from template cell K4)
* **Taxable Income** = Basic + OT − SSF (Employee)
* **PAYE** = Calculated from current slab table
* **Employer Contribution** = Basic × (rate from template cell Q4)
* **Deductions** = PAYE + SSF (Employee) + Loan Repayment
* **Net Pay** = Gross − Deductions
* Extra columns: **13.5% of Basic**, **5% of Basic**

Default tax slabs (7 brackets) are seeded automatically on first run.

---

## 🖥️ How to Use

1. **Login**
   Enter credentials to access the app.

2. **Generate Payroll Report**

   * Select an input Excel file
   * Choose Month and Year
   * Apply slabs & generate report
   * Report saved under the `reports/` folder and logged in DB

3. **Generate Payslips**

   * Pick a saved report
   * Enter a date (DD/MM/YYYY)
   * Choose destination folder
   * PDFs generated per staff

4. **Manage Reports & Payslips**

   * View, download, or delete items directly via the app

5. **Edit PAYE Slabs**

   * Open slab editor from the report screen
   * Add/remove/update brackets
   * Reset to default slabs if needed

---

## 📦 Packaging

The app can be packaged into an `.exe` using PyInstaller.
Resource resolution is handled so it runs seamlessly when frozen.


Do you also want me to include **screenshots placeholders** (like `![screenshot](docs/login.png)`) so the README looks more professional on GitHub?
```
