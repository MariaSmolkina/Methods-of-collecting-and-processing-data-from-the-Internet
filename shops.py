from selenium import webdriver
from pymongo import MongoClient
import pandas as pd


class ShopsParser:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['Shops']
        self.collection = self.db['Items']
        self.item_info = []

    def get_top_items_mvideo(self):
        driver = webdriver.Chrome('./chromedriver.exe')
        url = 'https://www.mvideo.ru/'
        driver.get(url)
        items = [i.get_attribute('href') for i in driver.find_elements_by_xpath('/html/body/div[2]/div/div[3]/div/'
                                                                                'div[4]/div/div[2]/div/div[1]/ul/li/'
                                                                                'div/div[3]/div/div/h3/a')]
        for i in items:
            driver.get(i)
            self.item_info.append({
                'url': i,
                'title': driver.find_element_by_class_name('fl-h1').text,
                'price': driver.find_element_by_class_name('fl-pdp-price__current').text,
                'image_url': driver.find_element_by_class_name('c-media-container__image').get_attribute('src'),
                })
        self.collection.insert_many(self.item_info)
        return pd.DataFrame(self.item_info).to_csv('mvideo_dump.csv')
        driver.close()

    def get_top_items_onlinetrade(self):
        driver = webdriver.Chrome('./chromedriver.exe')
        url = 'https://www.onlinetrade.ru/'
        driver.get(url)
        items = [i.get_attribute('href') for i in driver.find_elements_by_xpath('/html/body/div[1]/div/div[4]/div/'
                                                                                'div[7]/div/div[2]/div[2]/div/div/'
                                                                                'div/div[2]/div[2]/a')]
        for i in items:
            driver.get(i)
            self.item_info.append({
                'url': i,
                'title': driver.find_element_by_css_selector('h1').text,
                'price': driver.find_element_by_css_selector('span.js__actualPrice span').text,
                'image_url': driver.find_element_by_xpath('//*[@id="popupCatalogItem_bigImage"]').get_attribute('src'),
                })
        self.collection.insert_many(self.item_info)
        return pd.DataFrame(self.item_info).to_csv('mvideo_dump.csv')
        driver.close()


TopItems = ShopsParser()
TopItems.get_top_items_mvideo()
TopItems.get_top_items_onlinetrade()
