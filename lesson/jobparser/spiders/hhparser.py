import scrapy
from jobparser.items import Lesson5Item
import re
from pymongo import MongoClient


class HHSpider(scrapy.Spider):

    name = 'hhparser'
    allowed_domains = ['hh.ru']
    start_urls = ['https://spb.hh.ru//']

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['Vacancies']
        self.collection = self.db['hh_super_vacancies']

    def start_requests(self):
        url = 'https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&st=searchVacancy&text=' \
              '%D0%B4%D0%B0%D1%82%D0%B0+%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA'
        yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response, **kwargs):
        for href in response.css('a[href^="https://spb.hh.ru/vacancy/"]::attr(href)').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse)

    @staticmethod
    def get_min_max_salary(salary, required_value):
        salary_min = 'NaN'
        salary_max = 'NaN'
        salary_to_list = re.findall(r'\d+', str(salary))
        if len(salary_to_list) == 0:
            salary_min = 'NaN'
            salary_max = 'NaN'
        elif len(salary_to_list) == 2:
            if re.match(r'от', str(salary)) != None:
                salary_min = int(salary_to_list[0] + salary_to_list[1])
                salary_max = 'NaN'
            elif re.match(r'до', str(salary)) != None:
                salary_min = 'NaN'
                salary_max = int(salary_to_list[0] + salary_to_list[1])
            else:
                salary_min = int(salary_to_list[0] + salary_to_list[1])
                salary_max = int(salary_to_list[0] + salary_to_list[1])
        elif len(salary_to_list) == 4:
                salary_min = min(map(int, [salary_to_list[0] + salary_to_list[1],
                                           salary_to_list[2] + salary_to_list[3]]))
                salary_max = max(map(int, [salary_to_list[0] + salary_to_list[1],
                                           salary_to_list[2] + salary_to_list[3]]))
        if required_value == 'min':
            return salary_min
        elif required_value == 'max':
            return salary_max

    # Проверяет, имеется ли в базе указанная вакансия
    def _vacancy_is_exists(self, data):
        return bool(self.collection.find_one(data))

    def _add_to_db(self, data):
        if self._vacancy_is_exists(data):
            self.collection.update_one({'url': data['url']}, {'$set': data})
        else:
            self.collection.insert_one(data)

    def parse(self, response, **kwargs):
        vacancy_name = ''.join(response.css('h1[data-qa="vacancy-title"]::text').extract())
        salary = ''.join(response.css('p[class="vacancy-salary"] ::text').extract())
        salary_min = self.get_min_max_salary(salary, 'min')
        salary_max = self.get_min_max_salary(salary, 'max')
        url = response.request.url
        source = self.allowed_domains[0]
        yield self._add_to_db(Lesson5Item(vacancy_name=vacancy_name, salary=salary, salary_min=salary_min,
                                         salary_max=salary_max, url=url, source=source))
