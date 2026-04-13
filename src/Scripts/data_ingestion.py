import os
import json
import logging
import argparse
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataIngestor:
    def __init__(self, connection_string):
        self.conn_str = connection_string
        self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")

    def ingest_file(self, file_path, source_system):
        logger.info(f"Starting ingestion for file: {file_path}")
        
        try:
            # Detect file type
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Convert rows to JSON payloads and store in DB
            for index, row in df.iterrows():
                payload = row.to_json()
                self._save_raw_data(source_system, payload)
            
            logger.info(f"Successfully ingested {len(df)} records from {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {str(e)}")
            raise

    def _save_raw_data(self, source, payload):
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "{CALL usp_IngestRawData (?, ?, ?)}",
                source, payload, None
            )
            conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Ingest source data into SQL Server.")
    parser.add_argument("--file", required=True, help="Path to the source file")
    parser.add_argument("--source", required=True, help="Name of the source system")
    args = parser.parse_args()

    conn_str = os.getenv("SQL_CONNECTION_STRING", "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=EnterprisePortal;Uid=sa;Pwd=StrongPassword123;Encrypt=no;")
    
    ingestor = DataIngestor(conn_str)
    ingestor.ingest_file(args.file, args.source)

if __name__ == "__main__":
    main()
