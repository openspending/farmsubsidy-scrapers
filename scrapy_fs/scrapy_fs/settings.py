# Scrapy settings for scrapy_fs project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'scrapy_fs'

SPIDER_MODULES = ['scrapy_fs.spiders']
NEWSPIDER_MODULE = 'scrapy_fs.spiders'
# AUTOTHROTTLE_ENABLED = True

# ITEM_PIPELINES = {
#     'scrapy_fs.pipelines.FormatValidationPipeline': 100,
# }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_fs (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'