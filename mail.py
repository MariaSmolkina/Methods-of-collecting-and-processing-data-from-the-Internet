from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class EmailParser:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['Mail']
        self.collection = self.db['Messages']
        self.username = "email"
        self.password = "password"
        self.item_info = {}

    def _parse_element(self, element, xpath):
        result = WebDriverWait(element, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))).text
        return result

    def get_emails(self):
        driver = webdriver.Chrome('./chromedriver.exe')
        url = 'https://mail.ru/'
        driver.get(url)
        driver.find_element_by_xpath("/html/body/main/div[2]/div[1]/div[1]/div[2]/form[1]/div[1]/div[2]/"
                                     "input").send_keys(self.username)
        driver.find_element_by_xpath("/html/body/main/div[2]/div[1]/div[1]/div[2]/form[1]/button[1]").click()
        driver.implicitly_wait(10)
        driver.find_element_by_xpath("/html/body/main/div[2]/div[1]/div[1]/div[2]/form[1]/div[2]/"
                                     "input").send_keys(self.password)
        driver.find_element_by_xpath("/html/body/main/div[2]/div[1]/div[1]/div[2]/form[1]/button[2]").click()
        driver.implicitly_wait(10)
        items = [i.get_attribute('href') for i in driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[1]/'
                                                                                'div/div[2]/span/div[2]/div/div/div/'
                                                                                'div/div[1]/div/div/div[1]/div/div/div'
                                                                                '/a')]
        for i in items:
            driver.get(i)
            self.item_info = {
                'sender': driver.find_element_by_xpath('/html/body/div[5]/div/div[1]/div[1]/div/div[2]/span/'
                                                       'div[2]/div/div/div/div/div/div/div[2]/div[1]/div[1]'
                                                       '/div/div[2]/div[1]/span').text,
                'letter_date': driver.find_element_by_xpath('/html/body/div[5]/div/div[1]/div[1]/div/div[2]/'
                                                            'span/div[2]/div/div/div/div/div/div/div[2]/div[1]/'
                                                            'div[1]/div/div[2]/div[1]/div[1]').text,
                'subject': driver.find_element_by_xpath('/html/body/div[5]/div/div[1]/div[1]/div/div[2]/span/div[2]/'
                                                        'div/div/div/div/div/div/div[1]/div[3]/h2').text,
                'message': self._parse_element(driver, '/html/body/div[5]/div/div[1]/div[1]/div/div[2]/span/div[2]/'
                                                       'div/div/div/div/div/div/div[2]/div[1]/div[3]/div[2]/div/div/'
                                                       'div/div/div/div/div/div/div')
            }
            self.collection.insert_one(self.item_info)
        driver.close()


Emails = EmailParser()
Emails.get_emails()
