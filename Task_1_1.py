from bs4 import BeautifulSoup
import pandas as pd
import requests
from fake_headers import Headers
import html.parser
import re


def get_min_max_salary(salary, required_val):
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
                salary_list_min.append('NaN')
                salary_list_max.append('NaN')
        elif len(salary_to_list) == 4:
            salary_list_min.append(min(map(int, [salary_to_list[0] + salary_to_list[1], salary_to_list[2] + salary_to_list[3]])))
            salary_list_max.append(max(map(int, [salary_to_list[0] + salary_to_list[1], salary_to_list[2] + salary_to_list[3]])))
    if required_val == 'min':
        return salary_list_min
    elif required_val == 'max':
        return salary_list_max


def data_scraper_superjob(soup):
    vacancy_name = soup.find_all(class_='_6AfZ9')
    salary = soup.find_all(class_='_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW')
    salary_min = get_min_max_salary(salary, 'min')
    salary_max = get_min_max_salary(salary, 'max')
    vacancy_url = ['https://www.superjob.ru/' + i['href'] for i in soup.find_all('a', class_='_6AfZ9')]
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


def vacancy_to_list_superjob(vacancy, num_pages):
    vacancy_list = []
    for i in range(1, num_pages+1):
        params = {
            'keywords': vacancy,
            'profession_only': '1',
            'geo[c][0]': '15',
            'geo[c][1]': '1',
            'geo[c][2]': '9',
            'page': i
        }
        header = Headers(headers=True).generate()
        link = 'https://www.superjob.ru/vacancy/search/'
        url = requests.get(link, params=params, headers=header)
        if url.ok:
            soup = BeautifulSoup(url.text, 'html.parser')
            vacancy_list += data_scraper_superjob(soup)
        else:
            print('Check link')
    return vacancy_list


def data_scraper_hh(soup):
    vacancy_name = soup.find_all(class_='resume-search-item__name')
    salary = soup.find_all(class_='vacancy-serp-item__sidebar')
    salary_min = get_min_max_salary(salary, 'min')
    salary_max = get_min_max_salary(salary, 'max')
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


def vacancy_to_list_hh(vacancy, num_pages):
    vacancy_list = []
    for i in range(1, num_pages+1):
        params = {
            'text': vacancy,
            'page': i
        }
        header = Headers(headers=True).generate()
        link = 'https://spb.hh.ru/search/vacancy'
        url = requests.get(link, params=params, headers=header)
        if url.ok:
            soup = BeautifulSoup(url.text, 'html.parser')
            vacancy_list += data_scraper_hh(soup)
        else:
            print('Check link')
    return vacancy_list


def data_to_csv(data):
    total_data = []
    for i in data:
        total_data += i
    return pd.DataFrame(total_data).to_csv('dump.csv')


data_1 = vacancy_to_list_hh('Аналитик данных', 4)
data_2 = vacancy_to_list_superjob('Аналитик данных', 3)
data_list = [data_1, data_2]

data_to_csv(data_list)


