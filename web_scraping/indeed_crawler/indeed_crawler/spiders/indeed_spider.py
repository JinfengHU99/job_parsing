import os
import json
import scrapy
import re
import logging

class IndeedInfoSpider(scrapy.Spider):
    name = 'indeed_info'

    # Get the directory where the current file resides
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Read the configuration file using relative path
     config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..','config.json'))


    with open(config_path) as f:
        config = json.load(f)

    start_urls = [url for url in config['startUrl'] if url.startswith('https://fr.indeed.com')]
    
    # Initialize a set to store visited URLs
    visited_urls = set()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_search)

    def parse_search(self, response):
        offset = response.meta.get('offset', 0)
        current_page_url = response.url
        logging.debug(f"Processing page: {current_page_url}")
            
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        
        if script_tag:
            json_blob = json.loads(script_tag[0])

            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
            for index, job in enumerate(jobs_list):
                if job.get('jobkey') is not None:
                    job_url = 'https://fr.indeed.com/viewjob?jk=' + job.get('jobkey')+ '&tk=' + job.get('mobtk') + '&from=serp&vjs=3'
                    if job_url not in self.visited_urls:
                        self.visited_urls.add(job_url)
                        yield scrapy.Request(url=job_url, 
                                callback=self.parse_job, 
                                meta={  
                                    'page': round(offset / 10) + 1 if offset > 0 else 1,
                                    'position': index,
                                    'jobKey': job.get('jobkey'),
                                    'job_url': job_url,
                                    'current_page_url': current_page_url,
                                })

            # Check if there's a next page
            next_page_url = response.xpath('//a[@aria-label="Next Page"]/@href').get()
            if next_page_url:
                next_page_url = "https://fr.indeed.com" + next_page_url
                logging.debug(f"Next page URL found: {next_page_url}")
                yield scrapy.Request(url=next_page_url, callback=self.parse_search, meta={'offset': offset + 10})
            else:
                logging.debug("No more next pages.")

    def parse_job(self, response):
        job_url = response.meta.get('job_url')
        current_page_url = response.meta.get('current_page_url') 
        logging.debug(f"Current page URL: {current_page_url}")
        
        location_element = response.xpath("//div[@data-testid='inlineHeader-companyLocation']/div")
        location = location_element.xpath("text()").get() if location_element else None
            
        salary_element = response.xpath("//div[@id='salaryInfoAndJobType']/span[@class='css-19j1a75 eu4oa1w0']/text()")
        salary = salary_element.get() if salary_element else None
        
        type_element = response.xpath("//div[@id='salaryInfoAndJobType']/span[@class='css-k5flys eu4oa1w0']/text()")
        tp_list = [text.strip() for text in type_element.extract() if text.strip() and not text.strip().startswith("-")] if type_element else None
        tp = ", ".join(tp_list) if tp_list else None
        
        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        
        if script_tag:
            json_blob = json.loads(script_tag[0])
            job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]['jobInfoHeaderModel']
            sanitizedJobDescription= json_blob["jobInfoWrapperModel"]["jobInfoModel"]['sanitizedJobDescription']

            yield {
                'job-title': job.get('jobTitle'),
                'job-description-html': sanitizedJobDescription,
                'job-location': location,
                'job-salary': salary,
                'job-url': job_url,
                'job-type': tp,
            }
            
        logging.debug(f"Parsing job details for URL: {response.url}")
