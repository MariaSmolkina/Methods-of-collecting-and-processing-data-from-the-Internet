# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Lesson5Item(scrapy.Item):
    _id = scrapy.Field()
    vacancy_name = scrapy.Field()
    salary = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
