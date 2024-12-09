import os
import scrapy
import json
import re
import sys

class InsitooInfoSpider(scrapy.Spider):
    name = 'insitoo_info'
    
     # Get the directory where the current file resides
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Read the configuration file using relative path
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..','config.json'))

    with open(config_path) as f:
        config = json.load(f)

    start_urls = [url for url in config['startUrl'] if url.startswith('https://insitoo.com')]
    
    # Initialize a set to store visited URLs
    visited_urls = set()

    def parse(self, response):
        annonce_links = response.xpath('//div[@class="liste-missions"]/a/@href').extract()
        
        for link in annonce_links:
            if link not in self.visited_urls:
                self.visited_urls.add(link)
                yield response.follow(link, callback=self.parse_annonce)
                
        next_page_button = response.xpath('//a[@class="next page-numbers"]')
        if next_page_button:
            next_page_link = next_page_button.xpath('../@href').get()
            yield response.follow(next_page_link, callback=self.parse)
    
    def parse_annonce(self, response):
        # Parse the announcement page and extract necessary data
        title = response.xpath('//h3/text()').get()
        if title is None:
            self.logger.warning('No title found for the job annonce. Skipping...')
            return
#         descriptions = response.xpath('//div[@class="content-offer"]/p/text()').getall()
#         cleaned_descriptions = descriptions[3:-4] if len(descriptions) >= 7 else []
#         cleaned_descriptions = [desc.strip() for desc in cleaned_descriptions if desc.strip()]  # Remove whitespace and newline characters
#         if cleaned_descriptions and cleaned_descriptions[0].startswith(','):
#             cleaned_descriptions[0] = cleaned_descriptions[0][2:]
#         description = ' '.join(cleaned_descriptions) if cleaned_descriptions else None
        descriptions = response.xpath('//div[@class="content-offer"]/*').getall()
        cleaned_descriptions = descriptions[3:-4] if len(descriptions) >= 7 else []
        description = ''.join(cleaned_descriptions) if cleaned_descriptions else None
        target_string = "<p>Cette mission vous intéresse?</p>"
        if target_string in description:
            description = description.split(target_string)[0] + target_string
        location = response.xpath('//div[@class="detail"]/p[@class="lieu"]/text()').get(default=None)
        salary = response.xpath('//div[@class="detail"]/p[@class="price"]/text()').get(default=None)
                    
        url = response.url
        if url is None:
            self.logger.warning('No URL for the job annonce. Skipping...')
            return
        
        tp = "freelance"
        
        # Return the extracted data
        yield {
            'job-title': title,
            'job-description-html': description,
            'job-location': location,
            'job-salary': salary,
            'job-url': url,
            'job-type': tp
        }
        
