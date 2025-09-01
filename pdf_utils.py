import os, sys, calendar
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Use the bundled font file
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
TTF_PATH = os.path.join(BASE_DIR, 'BebasNeue.ttf')
pdfmetrics.registerFont(TTFont('BebasNeue', TTF_PATH))

# Load template from RESOURCE_DIR when frozen
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'PayAngel-Payroll-Template.pdf')

def generate_payslip_pdf(staff_id: str,
                         month: int,
                         year: int,
                         data_map: dict,
                         out_path: str):
    """
    Overlays payroll data onto the payslip PDF template.
    """
    reader = PdfReader(TEMPLATE_PATH)
    page = reader.pages[0]

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    # Report Label at top 
    report_label = f"{calendar.month_abbr[month]} {year}"
    can.setFont("BebasNeue", 30)
    can.setFillColorRGB(47/255, 57/255, 67/255)  # #2F3943
    can.drawString(320, 678, report_label)

    # User-entered date at (440, 630) 
    report_date = data_map.get('ReportDate', '')
    can.setFont("Times-Roman", 12)
    can.setFillColorRGB(0, 0, 0)
    can.drawString(440, 630, report_date)

    can.setFont("Times-Roman", 12)
    can.drawString(190, 630, data_map.get('Social Security No.', ''))
    can.drawString(120, 609, data_map.get('Tin No.', ''))

    can.setFont("Times-Bold", 14)
    can.drawString(110, 586, data_map.get('Name', ''))

    can.setFont("Times-Roman", 12)
    can.drawString(125, 566, data_map.get('STAFF ID', ''))

    # Financials
    can.drawString(397, 478, data_map.get('Basic Salary', ''))
    can.drawString(397, 452, data_map.get('SSF', ''))
    can.drawString(397, 428, data_map.get('Emp Cont', ''))
    can.drawString(397, 400, data_map.get('Allowances', ''))
    can.drawString(397, 375, data_map.get('OT', ''))

    can.setFont("Times-Bold", 12)
    can.drawString(397, 351, data_map.get('Taxable', ''))

    can.setFont("Times-Roman", 12)
    can.drawString(397, 323, data_map.get('PAYE', ''))
    can.drawString(397, 299, data_map.get('Loan Repayment', ''))

    can.setFont("Times-Bold", 12)
    can.drawString(397, 273, data_map.get('Net Pay', ''))

    can.setFont("Times-Roman", 12)
    can.drawString(250, 166, data_map.get('Percent13.5', ''))
    can.drawString(250, 127, data_map.get('Percent5', ''))

    can.save()
    packet.seek(0)

    overlay = PdfReader(packet)
    page.merge_page(overlay.pages[0])

    writer = PdfWriter()
    writer.add_page(page)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as f:
        writer.write(f)
