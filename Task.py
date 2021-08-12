from lxml import html
import requests
from fake_headers import Headers
import pandas as pd
import datetime


def get_news_mail_ru():

    header = Headers(headers=True).generate()
    url_mail = 'https://mail.ru/'

    response = requests.get(url_mail, headers=header)
    root = html.fromstring(response.text)

    news_url = root.xpath('''//*[@id="grid:middle"]/div[2]/div[3]/div[1]/ul/li[1]/a/@href | 
                            //*[@id="grid:middle"]/div[2]/div[3]/div[1]/ul/li[@data-testid="general-news-item"]/div[@class="news-item svelte-n3i2jw"]/a/@href''')

    news_text = root.xpath('''//*[@id="grid:middle"]/div[2]/div[3]/div[1]/ul/li[1]/a/div/p/text() |
                            //*[@id="grid:middle"]/div[2]/div[3]/div[1]/ul/li[@data-testid="general-news-item"]/div[@class="news-item svelte-n3i2jw"]/a/text()''')
    all_news_mail_info = []

    for i in range(len(news_text)):
        news_text[i] = news_text[i].replace(u'\xa0', u' ')
        news_text[0] = news_text[0].replace(u'\t\t\t\t\t', u'')

    for num, i in enumerate(news_text):
        all_news_mail_info.append({
            'Source': 'mail.ru',
            'News_text': i,
            'News_url': news_url[num],
            'Date information': 'No date information',
        })

    return all_news_mail_info


def get_news_lenta_ru():

    header = Headers(headers=True).generate()
    url_lenta = 'https://lenta.ru/'

    response = requests.get(url_lenta, headers=header)
    root = html.fromstring(response.text)

    news_url = root.xpath('''//*[@id="root"]/section[2]/div/div/div[1]/section[1]/div[2]/div[@class="item"]/a/@href''')
    news_text = root.xpath('''//*[@id="root"]/section[2]/div/div/div[1]/section[1]/div[2]/div[@class="item"]/a/text()''')
    news_datetime = root.xpath('''//*[@id="root"]/section[2]/div/div/div[1]/section[1]/div[2]//div[@class="item"]/a/time/@datetime''')

    all_news_lenta_info = []

    for num, i in enumerate(news_text):
        all_news_lenta_info.append({
            'Source': 'lenta.ru',
            'News_text': i,
            'News_url': url_lenta + news_url[num],
            'News_date': news_datetime[num],
        })

    return all_news_lenta_info


def get_yandex_news():

    header = Headers(headers=True).generate()
    url_yandex_news = 'https://yandex.ru/news/'

    response = requests.get(url_yandex_news, headers=header)
    root = html.fromstring(response.text)

    news_url = root.xpath('''//*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]/div[1]/article/div[2]/a/@href |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]/div[@class="mg-grid__col mg-grid__col_xs_4"]/article/div[1]/div[@class="mg-card__text"]/a/@href |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[3]/div[1]/article/div[1]/div/a/@href |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[3]/div[2]/div/div[@class="mg-grid__col mg-grid__col_xs_6"]/article/div[1]/div[1]/div/a/@href''')

    news_text = root.xpath('''//*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]/div[1]/article/div[2]/a/h2/text() |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]/div[@class="mg-grid__col mg-grid__col_xs_4"]/article/div[1]/div[@class="mg-card__text"]/a/h2/text() |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[3]/div[1]/article/div[1]/div/a/h2/text() |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[3]/div[2]/div/div[@class="mg-grid__col mg-grid__col_xs_6"]/article/div[1]/div[1]/div/a/h2/text()''')

    news_datetime = root.xpath('''//*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]/div[1]/article/div[2]/div[2]/div[1]/div/span[2]/text()|
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]/div[@class="mg-grid__col mg-grid__col_xs_4"]/article/div[3]/div[1]/div/span[2]/text() |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[3]/div[1]/article/div[3]/div[1]/div/span[2]/text() |
                            //*[@id="neo-page"]/div/div[2]/div/div[1]/div[3]/div[2]/div/div[@class="mg-grid__col mg-grid__col_xs_6"]/article/div[2]/div[1]/div/span[2]/text()''')

    all_yandex_news_info = []

    for num, i in enumerate(news_text):
        all_yandex_news_info.append({
            'Source': 'yandex.ru',
            'News_text': i,
            'News_url': news_url[num],
            'News_date': str(datetime.date.today()) + ',' + news_datetime[num],
        })

    return all_yandex_news_info


mail_news = get_news_mail_ru()
lenta_news = get_news_lenta_ru()
yandex_news = get_yandex_news()

news = mail_news + lenta_news + yandex_news

pd.DataFrame(news).to_csv('news_dump.csv')
