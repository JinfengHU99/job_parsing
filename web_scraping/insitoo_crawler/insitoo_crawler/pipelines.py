import csv
import os
from datetime import datetime
import sys

settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..','settings.py'))
sys.path.append(os.path.dirname(settings_path))

from settings import ROOT_PARSING_PATH


class CSVExportPipeline:
    def open_spider(self, spider):
        today_date = datetime.now().strftime('%Y-%m-%d')
        root_path = ROOT_PARSING_PATH
        folder_path = f'{root_path}/data/data_daily/{today_date}'
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f'insitoo_{current_time}.csv'
        file_path = os.path.join(folder_path, file_name)

        self.csv_file = open(file_path, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=[
            'job-title', 
            'job-description-html', 
            'job-location', 
            'job-salary', 
            'job-url',
            'job-type'
        ], delimiter=',')
        self.csv_writer.writeheader()

    def close_spider(self, spider):
        self.csv_file.close()

    def process_item(self, item, spider):
        self.csv_writer.writerow(item)
        return item

