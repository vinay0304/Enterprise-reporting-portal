import os
import logging
import argparse
import pandas as pd
import pyodbc
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, connection_string):
        self.conn_str = connection_string

    def generate_report(self, run_id):
        logger.info(f"Generating report for Run ID: {run_id}")
        
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                
                # Update status to Running
                cursor.execute("{CALL usp_UpdateReportStatus (?, ?, ?)}", run_id, "Running", None)
                
                # Fetch Report Info
                cursor.execute("SELECT report_name FROM report_runs WHERE run_id = ?", run_id)
                report_name = cursor.fetchone()[0]
                
                # Fetch Data
                df = pd.read_sql("SELECT * FROM validated_data", conn)
                
                # Create Output Directory
                output_dir = "reports/output"
                os.makedirs(output_dir, exist_ok=True)
                
                file_path = f"{output_dir}/Report_{run_id}.pdf"
                
                # Generate PDF
                self._create_pdf(file_path, report_name, df)
                
                # Update status to Completed
                cursor.execute("{CALL usp_UpdateReportStatus (?, ?, ?)}", run_id, "Completed", file_path)
                logger.info(f"Report {run_id} completed: {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to generate report {run_id}: {str(e)}")
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("{CALL usp_UpdateReportStatus (?, ?, ?)}", run_id, "Failed", None)

    def _create_pdf(self, path, title, df):
        c = canvas.Canvas(path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, f"Enterprise Report: {title}")
        
        c.setFont("Helvetica", 12)
        y = 700
        c.drawString(50, y, "Record ID | Entity Name | Amount | Date")
        y -= 20
        c.line(50, y, 550, y)
        y -= 20
        
        for index, row in df.head(20).iterrows():
            if y < 50:
                c.showPage()
                y = 750
            
            line = f"{row['record_id']} | {row['entity_name']} | ${row['amount']} | {row['transaction_date']}"
            c.drawString(50, y, line)
            y -= 15
            
        c.save()

def main():
    parser = argparse.ArgumentParser(description="Generate PDF report from SQL data.")
    parser.add_argument("--run_id", type=int, required=True, help="ID of the report run in database")
    args = parser.parse_args()

    conn_str = os.getenv("SQL_CONNECTION_STRING", "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=EnterprisePortal;Uid=sa;Pwd=StrongPassword123;Encrypt=no;")
    generator = ReportGenerator(conn_str)
    generator.generate_report(args.run_id)

if __name__ == "__main__":
    main()
