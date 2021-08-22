from scrapy.pipelines.images import ImagesPipeline
import scrapy
from scrapy import Request
from os.path import splitext
from pymongo import MongoClient
import os
from urllib.parse import urlparse


class LeroyMerlinImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for img in item['item_images']:
            yield scrapy.Request(img)
        return item

    # все изображения по товару загружаются в одну папку с названием "наименование товара"
    def file_path(self, request, response=None, info=None, item=None):
        name = item['item_name']
        return f'{name}/' + os.path.basename(urlparse(request.url).path)

class DataBasePipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['LeroyMerlin']

    def process_item(self, item, spider):
        collection = self.db['Items']
        collection.insert_one(item)
        return item
