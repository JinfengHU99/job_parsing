import os
from datetime import datetime
import sys

settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..','settings.py'))
sys.path.append(os.path.dirname(settings_path))

from settings import ROOT_PARSING_PATH,API_KEY_SCRAPEOPS


BOT_NAME = "indeed_crawler"

SPIDER_MODULES = ["indeed_crawler.spiders"]
NEWSPIDER_MODULE = "indeed_crawler.spiders"

ROBOTSTXT_OBEY = False

# ScrapeOps API Key
SCRAPEOPS_API_KEY = API_KEY_SCRAPEOPS

# Enable ScrapeOps Proxy
SCRAPEOPS_PROXY_ENABLED = True

# Add In The ScrapeOps Monitoring Extension
EXTENSIONS = {
'scrapeops_scrapy.extension.ScrapeOpsMonitor': 900, 
}


DOWNLOADER_MIDDLEWARES = {

    # ScrapeOps Monitor
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    
    # Proxy Middleware
    'indeed_crawler.middlewares.ScrapeOpsProxyMiddleware': 725,
}

# Max Concurrency On ScrapeOps Proxy Free Plan is 1 thread
CONCURRENT_REQUESTS = 1

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

LOG_LEVEL = 'DEBUG'

# Configure item pipelines
ITEM_PIPELINES = {
    'indeed_crawler.pipelines.CSVExportPipeline': 300,  
}

today_date = datetime.now().strftime('%Y-%m-%d')

CSV_OUTPUT_DIR = f"{ROOT_PARSING_PATH}/data/data_daily/{today_date}"

if not os.path.exists(CSV_OUTPUT_DIR):
    os.makedirs(CSV_OUTPUT_DIR)
    
