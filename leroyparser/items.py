# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Compose, MapCompose, TakeFirst


def parse_params(params):
    params = [i.strip().strip(':').replace('\xa0', ' ') for i in params]
    result = [item for item in params if item != '']
    result = dict(zip(result[::2], result[1::2]))
    return result


def parse_price(price):
    price = float(price[0])
    return price


class LeroyMerlinItem(scrapy.Item):
    _id = scrapy.Field()
    item_url = scrapy.Field(output_processor=TakeFirst())
    item_params = scrapy.Field(output_processor=Compose(parse_params))
    item_images = scrapy.Field()
    item_name = scrapy.Field(output_processor=TakeFirst())
    item_price = scrapy.Field(output_processor=parse_price)
