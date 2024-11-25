# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import os

class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            self.logger.info(f"Downloading image: {image_url}")
            yield Request(image_url, meta={'page_name': item['page_name']})

    def file_path(self, request, response=None, info=None):
        page_name = request.meta['page_name']
        image_name = os.path.basename(request.url)
        self.logger.info(f"Saving image: {page_name}/{image_name}")
        return f'{page_name}/{image_name}'
class SonosScraperPipeline:
    def process_item(self, item, spider):
        return item
