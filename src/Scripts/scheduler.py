import os
import logging
import subprocess
import argparse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
logger = logging.getLogger("Scheduler")

def run_script(script_name, args=None):
    cmd = ["python3", f"src/Scripts/{script_name}"]
    if args:
        cmd.extend(args)
    
    logger.info(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Script {script_name} failed with exit code {result.returncode}")
        logger.error(f"Stderr: {result.stderr}")
        return False
    
    logger.info(f"Script {script_name} completed successfully.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Enterprise Data Pipeline")
    parser.add_argument("--full-sync", action="store_true", help="Run ingestion, validation, and transformation")
    parser.add_argument("--file", help="Source file for ingestion")
    parser.add_argument("--source", help="Source system name")
    args = parser.parse_args()

    if args.full_sync:
        if args.file and args.source:
            # 1. Ingest
            if not run_script("data_ingestion.py", ["--file", args.file, "--source", args.source]):
                return
        
        # 2. Validate
        if not run_script("data_validation.py"):
            return
            
        # 3. Transform
        if not run_script("data_transformation.py"):
            return
            
        logger.info("Pipeline sync completed successfully.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
