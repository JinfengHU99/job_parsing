import os

ROOT_PARSING_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY_SCRAPEOPS = ""
API_KEY_OPENAI = ""

SPIDERS_PATHS = {
    'freelance': os.path.join(ROOT_PARSING_PATH, 'web_scraping/freelance_crawler/freelance_crawler/spiders'),
    'insitoo': os.path.join(ROOT_PARSING_PATH, 'web_scraping/insitoo_crawler/insitoo_crawler/spiders'),
    'indeed': os.path.join(ROOT_PARSING_PATH, 'web_scraping/indeed_crawler/indeed_crawler/spiders')
}

DATA_TOTAL_FOLDER = os.path.join(ROOT_PARSING_PATH, 'data/data_total')
DATA_DAILY_FOLDER = os.path.join(ROOT_PARSING_PATH, 'data/data_daily')
TOTAL_CSV_PATH = os.path.join(DATA_TOTAL_FOLDER, 'data_total.csv')
JSON_PATH = os.path.join(DATA_TOTAL_FOLDER, 'duplicates.json')
DUPLICATES_PATH = os.path.join(DATA_TOTAL_FOLDER, 'duplicates.csv')
FALSE_POSITIVES_PATH = os.path.join(DATA_TOTAL_FOLDER, 'false_positives.csv')


if not os.path.exists(DATA_TOTAL_FOLDER):
    os.makedirs(DATA_TOTAL_FOLDER)
    