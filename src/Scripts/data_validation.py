import os
import json
import logging
import argparse
import pyodbc
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, connection_string):
        self.conn_str = connection_string

    def validate_pending_records(self):
        logger.info("Starting validation for pending records...")
        
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            
            # Fetch pending records
            cursor.execute("SELECT raw_id, source_system, data_payload FROM raw_data WHERE status = 'Pending'")
            records = cursor.fetchall()
            
            if not records:
                logger.info("No pending records found.")
                return

            for raw_id, source, payload in records:
                self._validate_record(cursor, raw_id, source, payload)
            
            conn.commit()

    def _validate_record(self, cursor, raw_id, source, payload_json):
        try:
            data = json.loads(payload_json)
            errors = []

            # Rule 1: Required Fields
            if not data.get("id"):
                errors.append("Missing 'id' field")
            
            # Rule 2: Amount Range Check
            amount = data.get("total") or data.get("amount")
            if amount is not None:
                try:
                    if float(amount) < 0:
                        errors.append(f"Negative amount detected: {amount}")
                except ValueError:
                    errors.append(f"Invalid amount format: {amount}")
            else:
                errors.append("Amount is missing")

            # Rule 3: Entity Name Check
            if not data.get("entity"):
                errors.append("Entity name is missing")

            if errors:
                error_msg = "; ".join(errors)
                logger.warning(f"Record {raw_id} failed validation: {error_msg}")
                
                # Update status
                cursor.execute("UPDATE raw_data SET status = 'Failed' WHERE raw_id = ?", raw_id)
                
                # Log to Errors table
                cursor.execute(
                    "{CALL usp_LogValidationError (?, ?, ?, ?)}",
                    f"raw_id_{raw_id}", "DataValidation", error_msg, payload_json
                )
            else:
                logger.info(f"Record {raw_id} passed validation.")
                cursor.execute("UPDATE raw_data SET status = 'Validated' WHERE raw_id = ?", raw_id)

        except Exception as e:
            logger.error(f"Error processing record {raw_id}: {str(e)}")
            cursor.execute("UPDATE raw_data SET status = 'Error' WHERE raw_id = ?", raw_id)

def main():
    conn_str = os.getenv("SQL_CONNECTION_STRING", "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=EnterprisePortal;Uid=sa;Pwd=StrongPassword123;Encrypt=no;")
    validator = DataValidator(conn_str)
    validator.validate_pending_records()

if __name__ == "__main__":
    main()
