import scrapy
import os

class SonosGuidesSpider(scrapy.Spider):
    name = 'sonos_guides'
    start_urls = [
        'https://www.sonos.com/en-us/guides/arc',
        'https://www.sonos.com/en-us/guides/sonossystem',
        # Add more URLs as needed
    ]

    def parse(self, response):
        page_name = response.url.split('/')[-1]
        folder_path = f'output/{page_name}'
        os.makedirs(folder_path, exist_ok=True)

        # Extract all text content
        paragraphs = response.xpath('//p//text()').getall()
        headers = response.xpath('//h1//text() | //h2//text() | //h3//text()').getall()
        lists = response.xpath('//ul//li//text()').getall()

        # Save extracted content into separate files
        with open(f'{folder_path}/paragraphs.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(paragraphs))

        with open(f'{folder_path}/headers.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(headers))

        with open(f'{folder_path}/lists.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lists))