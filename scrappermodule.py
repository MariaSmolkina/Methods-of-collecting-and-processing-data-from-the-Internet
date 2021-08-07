from bs4 import BeautifulSoup
import pandas as pd
import requests
from fake_headers import Headers
import html.parser
import re
import json
from pprint import pprint
from pymongo import MongoClient


class ScrapingVacancy:

    def __init__(self, db_name, collection_name):
        self.header = Headers(headers=True).generate()
        self.hh_link = 'https://spb.hh.ru/search/vacancy'
        self.sj_link = 'https://www.superjob.ru/vacancy/search/'
        self.hh_vacancy_list = None
        self.sj_vacancy_list = None

        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

# Удаляет вакансию из базы данных
    def db_delete_vac(self, data):
        self.collection.remove(data)

# Добавляет новую вакансию или заменяет имеющуюся
    def _add_to_db(self, data):
        for vac in data:
            if self._vacancy_is_exists(vac):
                self.collection.update_one({'Url': vac['Url']}, {'$set': vac})
            else:
                self.collection.insert_one(vac)

# Формирует список факансий с требуемой зарплатой
    def find_salary_sample(self, salary):
        vacancies = self.collection.find({'Salary_min': {'$gt': salary}})
        self.data_to_csv(vacancies, 'vacancies')
        for vac in vacancies:
            pprint(vac)

# Проверяет, имеется ли в базе указанная вакансия
    def _vacancy_is_exists(self, data):
        return bool(self.collection.find_one(data))

# Формирует два списка: с мин и макс значениями зарплаты
    @staticmethod
    def get_min_max_salary(salary, required_value):
        salary_list_min = []
        salary_list_max = []
        for i in salary:
            salary_to_list = re.findall(r'\d+', str(i.text))
            if len(salary_to_list) == 0:
                salary_list_min.append('NaN')
                salary_list_max.append('NaN')
            elif len(salary_to_list) == 2:
                if re.match(r'от', str(i.text)) != None:
                    salary_list_min.append(int(salary_to_list[0] + salary_to_list[1]))
                    salary_list_max.append('NaN')
                elif re.match(r'до', str(i.text)) != None:
                    salary_list_min.append('NaN')
                    salary_list_max.append(int(salary_to_list[0] + salary_to_list[1]))
                else:
                    salary_list_min.append(int(salary_to_list[0] + salary_to_list[1]))
                    salary_list_max.append(int(salary_to_list[0] + salary_to_list[1]))
            elif len(salary_to_list) == 4:
                salary_list_min.append(
                    min(map(int, [salary_to_list[0] + salary_to_list[1], salary_to_list[2] + salary_to_list[3]])))
                salary_list_max.append(
                    max(map(int, [salary_to_list[0] + salary_to_list[1], salary_to_list[2] + salary_to_list[3]])))
        if required_value == 'min':
            return salary_list_min
        elif required_value == 'max':
            return salary_list_max

# Сохраняет данные в csv
    @staticmethod
    def data_to_csv(data, file_name):
        return pd.DataFrame(data).to_csv(f'{file_name}_dump.csv')

# Сохраняет данные в json
    @staticmethod
    def data_to_json(data):
        with open('data.json', 'w') as f:
            json.dump(data, f)

# Парсинг сайтов
    def search_vacancy(self, vacancy, pages):
        self._vacancy_to_list_hh(vacancy, pages)
        self._vacancy_to_list_superjob(vacancy, pages)

# Парсинг hh
    def _vacancy_to_list_hh(self, vacancy, pages):
        self.hh_vacancy_list = []
        for i in range(1, pages + 1):
            params = {
                'text': vacancy,
                'page': i
            }
            url = requests.get(self.hh_link, params=params, headers=self.header)
            if url.ok:
                soup = BeautifulSoup(url.text, 'html.parser')
                self.hh_vacancy_list += self._data_scraper_hh(soup)
            else:
                print('Check link')
        self._add_to_db(self.hh_vacancy_list)
        return self.data_to_csv(self.hh_vacancy_list, 'hh')

    def _data_scraper_hh(self, soup):
        vacancy_name = soup.find_all(class_='resume-search-item__name')
        salary = soup.find_all(class_='vacancy-serp-item__sidebar')
        salary_min = self.get_min_max_salary(salary, 'min')
        salary_max = self.get_min_max_salary(salary, 'max')
        vacancy_url = [i['href'] for i in soup.find_all(href=re.compile("https://spb.hh.ru/vacancy/"))]
        employer_name = soup.find_all(class_='vacancy-serp-item__meta-info-company')
        employer_address = soup.find_all(class_='vacancy-serp-item__meta-info')
        vacancy_description = soup.find_all(class_='g-user-content')
        all_vacancies_hh_info = []
        for num, i in enumerate(vacancy_name):
            all_vacancies_hh_info.append({
                'Vacancy': i.text,
                'Salary': salary[num].text,
                'Salary_min': salary_min[num],
                'Salary_max': salary_max[num],
                'Employer': employer_name[num].text,
                'Location': employer_address[num].text,
                'Description': vacancy_description[num].text,
                'Url': vacancy_url[num],
                'Site': 'hh.ru',
            })
        return all_vacancies_hh_info

# Парсинг superjob
    def _data_scraper_superjob(self, soup):
        vacancy_name = soup.find_all(class_='_6AfZ9')
        salary = soup.find_all(class_='_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW')
        salary_min = self.get_min_max_salary(salary, 'min')
        salary_max = self.get_min_max_salary(salary, 'max')
        vacancy_url = [self.sj_link + i['href'] for i in soup.find_all('a', class_='_6AfZ9')]
        employer_name = soup.find_all(class_='f-test-text-vacancy-item-company-name')
        employer_address = [re.split(r' • ', str(i.text))[1] for i in
                            soup.find_all(class_='f-test-text-company-item-location')]
        vacancy_description = soup.find_all(class_='_1h3Zg _38T7m e5P5i _2hCDz _2ZsgW _2SvHc')
        all_vacancies_superjob_info = []
        for num, i in enumerate(vacancy_name):
            all_vacancies_superjob_info.append({
                'Vacancy': i.text,
                'Salary': salary[num].text,
                'Salary_min': salary_min[num],
                'Salary_max': salary_max[num],
                'Employer': employer_name[num].text,
                'Location': employer_address[num],
                'Description': vacancy_description[num].text,
                'Url': vacancy_url[num],
                'Site': 'superjob.ru',
            })
        return all_vacancies_superjob_info

    def _vacancy_to_list_superjob(self, vacancy, pages):
        self.sj_vacancy_list = []
        for i in range(1, pages + 1):
            params = {
                'keywords': vacancy,
                'profession_only': '1',
                'geo[c][0]': '15',
                'geo[c][1]': '1',
                'geo[c][2]': '9',
                'page': i
            }
            url = requests.get(self.sj_link, params=params, headers=self.header)
            if url.ok:
                soup = BeautifulSoup(url.text, 'html.parser')
                self.sj_vacancy_list += self._data_scraper_superjob(soup)
            else:
                print('Check link')
        self._add_to_db(self.sj_vacancy_list)
        return self.data_to_csv(self.sj_vacancy_list, 'sj')