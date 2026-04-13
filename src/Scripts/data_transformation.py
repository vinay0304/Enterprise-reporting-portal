import os
import json
import logging
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, connection_string):
        self.conn_str = connection_string

    def transform_records(self):
        logger.info("Starting data transformation...")
        
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            
            # Fetch validated but not yet transformed records
            cursor.execute("""
                SELECT raw_id, data_payload 
                FROM raw_data 
                WHERE status = 'Validated' 
                AND raw_id NOT IN (SELECT raw_reference_id FROM validated_data)
            """)
            records = cursor.fetchall()
            
            if not records:
                logger.info("No records to transform.")
                return

            for raw_id, payload_json in records:
                self._transform_and_insert(cursor, raw_id, payload_json)
            
            conn.commit()

    def _transform_and_insert(self, cursor, raw_id, payload_json):
        try:
            data = json.loads(payload_json)
            
            # Normalize Fields
            external_id = str(data.get("id", f"RAW-{raw_id}"))
            entity_name = str(data.get("entity", "Unknown")).strip().title()
            entity_type = "Enterprise" if data.get("total", 0) > 1000 else "General"
            amount = float(data.get("total", data.get("amount", 0)))
            
            # Handle Date
            date_str = data.get("date")
            try:
                trans_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
            except ValueError:
                trans_date = datetime.now().date()

            # Insert into ValidatedData
            cursor.execute("""
                INSERT INTO validated_data (external_id, entity_name, entity_type, amount, transaction_date, raw_reference_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, external_id, entity_name, entity_type, amount, trans_date, raw_id)
            
            logger.info(f"Transformed record {raw_id} -> {entity_name}")

        except Exception as e:
            logger.error(f"Transformation failed for raw_id {raw_id}: {str(e)}")

def main():
    conn_str = os.getenv("SQL_CONNECTION_STRING", "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=EnterprisePortal;Uid=sa;Pwd=StrongPassword123;Encrypt=no;")
    transformer = DataTransformer(conn_str)
    transformer.transform_records()

if __name__ == "__main__":
    main()
