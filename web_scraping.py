from concurrent.futures import ThreadPoolExecutor
from settings import SPIDERS_PATHS, DATA_TOTAL_FOLDER, DATA_DAILY_FOLDER, TOTAL_CSV_PATH
import subprocess
import os
import logging
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to run spiders concurrently
def run_spider(spider, path):
    try:
        subprocess.run(["scrapy", "crawl", f"{spider}_info"], cwd=path, check=True)
        logging.info(f"Successfully ran spider: {spider}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running spider {spider}: {e}")

# Execute spiders concurrently with a maximum of 5 workers
with ThreadPoolExecutor(max_workers=5) as executor:
    for spider, path in SPIDERS_PATHS.items():
        if not os.path.exists(path):
            logging.warning(f"Path for spider {spider} does not exist: {path}")
            continue
        executor.submit(run_spider, spider, path)

# Function to update the total data by merging daily data
def update_total_data(data_total_folder, data_daily_folder, TOTAL_CSV_PATH):
    # Check if the total CSV file exists
    if os.path.exists(TOTAL_CSV_PATH):
        total_data = pd.read_csv(TOTAL_CSV_PATH)
        logging.info("Loaded existing total data.")
    else:
        # Create a new DataFrame with column names if the file doesn't exist
        total_data = pd.DataFrame(columns=['job-title', 'job-description-html', 'job-location', 'job-salary', 'job-url', 'job-type', 'import-date', 'platform'])
        logging.info("Created new total data DataFrame.")

    # Find the latest daily folder based on the folder name (assuming the folder name is a date)
    try:
        latest_daily_folder = max(
            [folder for folder in os.listdir(DATA_DAILY_FOLDER) if os.path.isdir(os.path.join(DATA_DAILY_FOLDER, folder))],
            key=lambda folder: datetime.strptime(folder, "%Y-%m-%d")  # Assuming the folder name is in "YYYY-MM-DD" format
        )
        latest_daily_folder_path = os.path.join(DATA_DAILY_FOLDER, latest_daily_folder)
        logging.info(f"Found latest daily folder: {latest_daily_folder}")
    except ValueError as e:
        logging.error(f"Error finding latest daily folder: {e}")
        return

    # Get all CSV files in the latest daily folder
    all_csv_files = [file for file in os.listdir(latest_daily_folder_path) if file.endswith('.csv')]
    if not all_csv_files:
        logging.warning(f"No CSV files found in {latest_daily_folder_path}")
        return

    # Read and merge all CSV files from the latest daily folder
    for file_name in all_csv_files:
        file_path = os.path.join(latest_daily_folder_path, file_name)
        daily_data = pd.read_csv(file_path)
        total_data = pd.concat([total_data, daily_data], ignore_index=True)
        logging.info(f"Merged data from {file_name} into total data.")

    # Remove duplicates based on 'job-url' column
    total_data = total_data.drop_duplicates(subset=['job-url'])
    logging.info(f"Removed duplicates. Total data now has {len(total_data)} rows.")

    # Save the updated total data back to the CSV file
    total_data.to_csv(TOTAL_CSV_PATH, index=False)
    logging.info(f"Updated total data saved to {TOTAL_CSV_PATH}")

# Call the function to update the total data (for example, passing the correct paths)
update_total_data(DATA_TOTAL_FOLDER, DATA_DAILY_FOLDER, TOTAL_CSV_PATH)
