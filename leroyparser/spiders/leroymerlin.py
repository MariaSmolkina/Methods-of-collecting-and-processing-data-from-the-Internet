import scrapy
from leroyparser.items import LeroyMerlinItem
from scrapy.loader import ItemLoader


class LeroyMerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://https://leroymerlin.ru/']
    num_pages = 2

    def start_requests(self):
        for page in range(1, 1 + self.num_pages):
            url = f'https://leroymerlin.ru/catalogue/dekor/?page={page}'
            yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response, **kwargs):
        for href in response.css('div[class="phytpj4_plp largeCard"] a[href^="/product/"]::attr(href)').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        l = ItemLoader(item=LeroyMerlinItem(), response=response)
        l.add_css('item_name', 'h1[class="header-2"] ::text'),
        l.add_value('item_url', response.url)
        l.add_css('item_params', 'dl[class="def-list"] ::text')
        l.add_css('item_price', 'meta[itemprop="price"] ::attr(content)')
        l.add_css('item_images', 'img[alt="product image"] ::attr(src)')
        yield l.load_item()
