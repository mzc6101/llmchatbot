import scrapy
import os
import json

class SonosGuidesSpider(scrapy.Spider):
    name = 'sonos_guides'
    start_urls = [
        'https://www.sonos.com/en-us/guides/arc',
        'https://www.sonos.com/en-us/guides/sonossystem',
        'https://www.sonos.com/en-us/guides/sonosace',
        'https://www.sonos.com/en-us/guides/era300',
        'https://www.sonos.com/en-us/guides/era100',
        'https://www.sonos.com/en-us/guides/roam2',
        'https://www.sonos.com/en-us/guides/roam',
        'https://www.sonos.com/en-us/guides/roamsl',
        'https://www.sonos.com/en-us/guides/move2',
        'https://www.sonos.com/en-us/guides/move',
        'https://www.sonos.com/en-us/guides/arcultra',
        'https://www.sonos.com/en-us/guides/arc',
        'https://www.sonos.com/en-us/guides/arcsl',
        'https://www.sonos.com/en-us/guides/beam',
        'https://www.sonos.com/en-us/guides/ray',
        'https://www.sonos.com/en-us/guides/sub',
        'https://www.sonos.com/en-us/guides/sub3',
        'https://www.sonos.com/en-us/guides/submini',
        'https://www.sonos.com/en-us/guides/five',
        'https://www.sonos.com/en-us/guides/one',
        'https://www.sonos.com/en-us/guides/onesl',
        'https://www.sonos.com/en-us/guides/era100pro',
        'https://www.sonos.com/en-us/guides/amp',
        'https://www.sonos.com/en-us/guides/boost',
        'https://www.sonos.com/en-us/guides/port',
        'https://www.sonos.com/en-us/guides/s1',
        # Add more URLs as needed
    ]

    def parse(self, response):
        # Extract page name for folder naming
        page_name = response.url.split('/')[-1]
        folder_path = f'output/{page_name}'
        os.makedirs(folder_path, exist_ok=True)

        # Extract text content
        paragraphs = response.xpath('//p//text()').getall()
        headers = response.xpath('//h1//text() | //h2//text() | //h3//text()').getall()
        lists = response.xpath('//ul//li//text()').getall()

        # Consolidate data into a dictionary
        data = {
            'paragraphs': paragraphs,
            'headers': headers,
            'lists': lists
        }

        # Save consolidated data into a JSON file
        json_path = os.path.join(folder_path, 'data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # Extract image URLs and yield them for the pipeline
        image_urls = response.xpath('//img/@src').getall()
        for img_url in image_urls:
            img_url = response.urljoin(img_url)  # Convert relative URLs to absolute
            self.log(f'Image URL: {img_url}')  # Log image URLs
            yield {
                'image_urls': [img_url],
                'page_name': page_name,
            }

        self.log(f'Data saved for {page_name}')