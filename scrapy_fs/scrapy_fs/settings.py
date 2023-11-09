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
#     'scrapy_fs.pipelines.DropSubsidyFilter': 100,
# }

USER_AGENT = 'Farm subsidy scraper bot (https://farmsubsidy.org)'

# For EE
URLLENGTH_LIMIT=6000
