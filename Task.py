import scrappermodule

Vacancy = scrappermodule.ScrapingVacancy('Data_analyst_vacancies', 'vacancies')
# Vacancy.db_delete_vac({})
Vacancy.search_vacancy('Аналитик данных', 2)
Vacancy.find_salary_sample(60000)  # делает dump с данными в файл vacancies_dump

