import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
import re
import subprocess
import settings
import web_scraping
import dect_duplicates
import categorization
import false_positives
from false_positives import CyberProcessor
import datetime

def extract_platform(filename):
    # Extract platform name from the filename
    platform = filename.split('_')[0]
    return platform

def remove_blank_lines(text):
    # Remove blank lines from the text
    return '\n'.join([line.strip() for line in text.split('\n') if line.strip()])

def update_total_data(data_total_folder, data_daily_folder, total_csv_path):
    # Check if the total CSV file exists
    if os.path.exists(total_csv_path):
        total_data = pd.read_csv(total_csv_path)
    else:
        # Create a new DataFrame with column names if the file doesn't exist
        total_data = pd.DataFrame(columns=['job-title', 'job-description-html', 'job-location', 'job-salary', 'job-url', 'job-type', 'import-date', 'platform'])
  
    # Find the latest daily folder
    latest_daily_folder = max([folder for folder in os.listdir(data_daily_folder) if os.path.isdir(os.path.join(data_daily_folder, folder))], key=pd.to_datetime)
    latest_daily_folder_path = os.path.join(data_daily_folder, latest_daily_folder)

    # Get all CSV files in the latest daily folder
    all_csv_files = [file for file in os.listdir(latest_daily_folder_path) if file.endswith('.csv')]

    # Group files by platform name
    platform_files = {}
    for file in all_csv_files:
        platform = extract_platform(file)
        if platform not in platform_files:
            platform_files[platform] = []
        platform_files[platform].append(file)

    # Iterate over each platform, find the latest file, and load data
    for platform, files in platform_files.items():
        latest_file = max(files)
        latest_file_path = os.path.join(latest_daily_folder_path, latest_file)
        latest_data = pd.read_csv(latest_file_path)
        
        # Process job-description column to remove HTML tags
#         latest_data['job-description'] = latest_data['job-description'].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
        
        # Process job-description column to replace '?' with "'"
        latest_data['job-description-html'] = latest_data['job-description-html'].apply(lambda x: re.sub(r'([A-Za-z])\?([A-Za-zÀ-ÖØ-öø-ÿ]+)', r'\1\'\2', x))
        latest_data['job-description-html'] = latest_data['job-description-html'].str.replace('\\', '', regex=False)
        
        # Remove blank lines from job-description column
        latest_data['job-description-html'] = latest_data['job-description-html'].apply(remove_blank_lines)
        
        # Add the latest data to the total DataFrame and mark the platform
        latest_data['platform'] = platform
        latest_data['import-date'] = latest_daily_folder
        total_data = pd.concat([total_data, latest_data], ignore_index=True)
        
        # Detect duplicate url
        duplicate_url = total_data.duplicated(subset=['job-url']).any()
        if duplicate_url:
            total_data.drop_duplicates(subset=['job-url'], keep='first', inplace=True)
    print("Finish the duplicate url detection.")
    
    # Delete empty description lines
    total_data.dropna(subset=['job-description-html'], inplace=True)
    total_data.reset_index(drop=True, inplace=True)
        
    # Detect duplicate data
    total_data = dect_duplicates.detect_duplicate(total_data)
    print("Finish the clean data.")
      
    
    if len(sys.argv) > 1 and sys.argv[1] == "cat_enabled":
        # Check if 'category' column is empty and update it if necessary
        if 'category' not in total_data.columns or total_data['category'].isnull().all():             
            total_data['category'] = category.generate_categories(total_data)
#             
        if 'category' in total_data.columns and total_data['category'].isnull().any():
            # Generate categories for rows with missing 'category'
            mask = total_data['category'].isnull()
            total_data.loc[mask, 'category'] = category.generate_categories(total_data[mask])

    # Detect faux positif
    # Delect no freelance
    total_data = fauxpositif.delete_no_freelance(total_data)
    # Delect not belong to cyber (ChatGPT)
    if len(sys.argv) > 1 and sys.argv[1] == "cyber_enabled":
        processor = CyberProcessor()
        total_data = processor.delete_non_cyber(total_data)    
     
    # Write the updated total DataFrame to the CSV file
    total_data.to_csv(total_csv_path, index=False)
    print(f"Successfully imported the latest data into '{total_csv_path}'.")
       
    # Filter and store the data for uploading (latest unique import-date)
    unique_import_dates = total_data['import-date'].unique()
    if len(unique_import_dates) == 1:
        latest_import_date = unique_import_dates[0]
        data_uploading = total_data[total_data['import-date'] == latest_import_date]
        
        # Ensure only one unique import-date
        if len(data_uploading['import-date'].unique()) == 1:
            data_uploading_filename = f"data_uploading_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            data_uploading_filepath = os.path.join(data_total_folder, data_uploading_filename)
            data_uploading.to_csv(data_uploading_filepath, index=False)
            print(f"Successfully exported the newly loaded data to '{data_uploading_filepath}'.")
        else:
            print("Error: Multiple unique import-dates found in data_uploading.")
    else:
        print("Error: Multiple unique import-dates found in total_data.")

    
if __name__ == "__main__":
     # Run the web scraping process at the start
    print("Starting web scraping...")
    web_scraping.run_web_scraping() 

    # Call the function to update the total CSV file
    update_total_data(settings.DATA_TOTAL_FOLDER, settings.DATA_DAILY_FOLDER, settings.TOTAL_CSV_PATH)
    print("Successfully update the data.")
    print("Finish")