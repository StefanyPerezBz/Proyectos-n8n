from fpdf import FPDF
from datetime import datetime
import os

class PDFReport:
    @staticmethod
    def generate(title: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=title, ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(200, 10, txt="Este reporte contiene un resumen de las detecciones de phishing.", ln=True)
        os.makedirs("reports", exist_ok=True)
        path = f"reports/reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(path)
        return path
