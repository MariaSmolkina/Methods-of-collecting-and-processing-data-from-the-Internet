
BOT_NAME = 'leroyparser'

SPIDER_MODULES = ['leroyparser.spiders']
NEWSPIDER_MODULE = 'leroyparser.spiders'

ROBOTSTXT_OBEY = False
LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'

DOWNLOAD_DELAY = 0

ITEM_PIPELINES = {
   'leroyparser.pipelines.DataBasePipeline': 2,
   'leroyparser.pipelines.LeroyMerlinImagesPipeline': 1,
}

IMAGES_STORE = r'downloaded'
