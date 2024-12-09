import scrapy
import json
import os
import spacy
import sys

nlp = spacy.load("fr_core_news_sm")

class FreelanceInfoSpider(scrapy.Spider):
    name = 'freelance_info'

    # Get the directory where the current file resides
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Read the configuration file using relative path
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..','config.json'))

    with open(config_path) as f:
        config = json.load(f)

    start_urls = [url for url in config['startUrl'] if url.startswith('https://www.free-work.com')]
    
    # Initialize a set to store visited URLs
    visited_urls = set()

    def parse(self, response):
        # Extract announcement links
        annonce_links = response.xpath('//a/@href').extract()
        
        for link in annonce_links:    
            if not link.startswith('javascript:') and link not in self.visited_urls:
                self.visited_urls.add(link)
                yield response.follow(link, callback=self.parse_annonce)

        
        # Iterate through announcement links and send requests
        next_page_button = response.xpath('//button[text()="Suivant"]')
        if next_page_button:
            next_page_link = next_page_button.xpath('../@href').get()
            yield response.follow(next_page_link, callback=self.parse)

        

    def parse_annonce(self, response):
        # Parse the announcement page and extract necessary data
        title = response.xpath('//span[@class="hidden md:block"]/text()').get()
        if title is None:
            self.logger.warning('No title found for the job annonce. Skipping...')
            return
        descriptions = response.xpath('//div[@class="html-renderer prose-content"]/*').getall()
        description = ''.join(descriptions) if descriptions else None
        if "- Environnement technique de la mission :" in description:
            description = description.split("- Environnement technique de la mission :")[0].strip()
        location = None
        salary = None
        for element in response.xpath("//div[@class='grid']/div[contains(@class, 'flex')]/span[@class='w-full text-sm line-clamp-2']/text()"):
            text = element.extract().strip()
            if "€⁄j" in text:
                if "€⁄an," in text:
                    salary = text.split("€⁄an,")[1].strip()
                else:
                    salary = text
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "LOC":
                    location = text
                    
        url = response.url
        if url is None:
            self.logger.warning('No URL for the job annonce. Skipping...')
            return
        
        tp_nodes = response.xpath("//div[@class='tags relative w-full']/span/div//text()")
        tp = ' '.join(tp_nodes.extract()) if tp_nodes else None
            
        
        # Return the extracted data
        yield {
            'job-title': title,
            'job-description-html': description,
            'job-location': location,
            'job-salary': salary,
            'job-url': url,
            'job-type': tp
        }
        
        self.logger.info(f'Title: {title}, Description: {description}, Location: {location}, Salary: {salary}, URL: {url}, Type: {tp}' )
