<p class="has-line-data" data-line-start="0" data-line-end="1"><strong>Payroll App</strong></p>
<p class="has-line-data" data-line-start="2" data-line-end="3">A desktop GUI (Tkinter) tool to generate monthly Payroll Reports and individual Payslips from an Excel input, with configurable PAYE tax slabs, SSF/Tier calculations, and a tiny SQLite database to track outputs.</p>
<p class="has-line-data" data-line-start="4" data-line-end="5"><strong>Features:</strong></p>
<ol>
<li class="has-line-data" data-line-start="6" data-line-end="7">Generate Payroll Report from a staff Excel file using a bundled template</li>
<li class="has-line-data" data-line-start="7" data-line-end="8">Generate Payslips (PDF) for each staff member from a selected report</li>
<li class="has-line-data" data-line-start="8" data-line-end="9">Edit PAYE tax slabs (add/remove/update, reset to defaults)</li>
<li class="has-line-data" data-line-start="9" data-line-end="10">View / Download / Delete previously generated reports &amp; payslips</li>
<li class="has-line-data" data-line-start="10" data-line-end="11">Login screen (basic credentials from config.ini)</li>
<li class="has-line-data" data-line-start="11" data-line-end="12">Portable storage: SQLite DB + output folders live in app data</li>
<li class="has-line-data" data-line-start="12" data-line-end="14">Packagable with PyInstaller (resources resolved when frozen)</li>
</ol>
<p class="has-line-data" data-line-start="14" data-line-end="15"><strong>Tech Stack</strong></p>
<ol>
<li class="has-line-data" data-line-start="16" data-line-end="17">Python 3.10+</li>
<li class="has-line-data" data-line-start="17" data-line-end="18">Tkinter, ttk</li>
<li class="has-line-data" data-line-start="18" data-line-end="19">pandas, openpyxl</li>
<li class="has-line-data" data-line-start="19" data-line-end="20">reportlab, PyPDF2</li>
<li class="has-line-data" data-line-start="20" data-line-end="21">sqlite3</li>
<li class="has-line-data" data-line-start="21" data-line-end="23">PyInstaller for packaging</li>
</ol>
<p class="has-line-data" data-line-start="23" data-line-end="24"><strong>Run the App (Dev)</strong></p>
<p class="has-line-data" data-line-start="25" data-line-end="27">python <a href="http://main.py">main.py</a><br>
First launch creates the DB and shows the Login screen (default admin / password123).</p>
<p class="has-line-data" data-line-start="28" data-line-end="29"><strong>Input Excel Format (exact columns, order)</strong></p>
<p class="has-line-data" data-line-start="30" data-line-end="31">The payroll generator expects the following header row (case &amp; order must match):</p>
<ol>
<li class="has-line-data" data-line-start="32" data-line-end="33">Name</li>
<li class="has-line-data" data-line-start="33" data-line-end="34">STAFF ID</li>
<li class="has-line-data" data-line-start="34" data-line-end="35">Social Security No.</li>
<li class="has-line-data" data-line-start="35" data-line-end="36">Tin No.</li>
<li class="has-line-data" data-line-start="36" data-line-end="37">POSITION</li>
<li class="has-line-data" data-line-start="37" data-line-end="38">Basic Salary</li>
<li class="has-line-data" data-line-start="38" data-line-end="39">Allowances</li>
<li class="has-line-data" data-line-start="39" data-line-end="40">OT</li>
<li class="has-line-data" data-line-start="40" data-line-end="42">Loan Repayment</li>
</ol>
<p class="has-line-data" data-line-start="42" data-line-end="43"><strong>What gets computed</strong></p>
<ol>
<li class="has-line-data" data-line-start="44" data-line-end="45">Gross = Basic Salary + Allowances + OT</li>
<li class="has-line-data" data-line-start="45" data-line-end="46">SSF (employee) = Basic * K4 (rate from template cell K4)</li>
<li class="has-line-data" data-line-start="46" data-line-end="47">Taxable = Basic + OT − SSF (employee)</li>
<li class="has-line-data" data-line-start="47" data-line-end="48">PAYE = Calculated in Python from current slab table</li>
<li class="has-line-data" data-line-start="48" data-line-end="49">Employer Contribution = Basic * Q4 (rate from template cell Q4)</li>
<li class="has-line-data" data-line-start="49" data-line-end="50">Deductions = PAYE + SSF (employee) + Loan Repayment</li>
<li class="has-line-data" data-line-start="50" data-line-end="51">Net Pay = Gross − Deductions</li>
<li class="has-line-data" data-line-start="51" data-line-end="53">Extra columns: 13.5% of Basic and 5% of Basic</li>
</ol>
<p class="has-line-data" data-line-start="53" data-line-end="54">Default tax slabs are seeded on first run (7 brackets). You can edit slabs at runtime and/or reset to defaults.</p>
<p class="has-line-data" data-line-start="55" data-line-end="56"><strong>How to Use (GUI)</strong></p>
<ol>
<li class="has-line-data" data-line-start="57" data-line-end="58">Login</li>
<li class="has-line-data" data-line-start="58" data-line-end="63">Generate Report<br>
a. Choose the input Excel file<br>
b. Pick Month and Year<br>
c. Click Apply Slabs &amp; Generate<br>
d. The report is saved under the app’s reports folder and recorded in the DB</li>
<li class="has-line-data" data-line-start="63" data-line-end="67">Generate Payslips<br>
a. Select a report (e.g., APR 2025)<br>
b. Enter a date as DD/MM/YYYY (appears on the payslips)<br>
c. Choose a destination folder; PDFs for each staff are created</li>
<li class="has-line-data" data-line-start="67" data-line-end="69">View / Download / Delete:<br>
a.Use View Reports / Payslips to open, copy, or delete items</li>
</ol>
<p class="has-line-data" data-line-start="71" data-line-end="72"><strong>Editing PAYE Slabs</strong></p>
<ol>
<li class="has-line-data" data-line-start="73" data-line-end="74">Edit PAYE Slabs from the Report screen</li>
<li class="has-line-data" data-line-start="74" data-line-end="78">Rules enforced:<br>
a. Final slab must have blank “To” (open-ended)<br>
b. Only one open-ended slab allowed<br>
c. Each row’s From must match the previous row’s To</li>
<li class="has-line-data" data-line-start="78" data-line-end="79">Reset restores the original 7-bracket defaults</li>
</ol>
