""" This is the scraper for Croatia. """


from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class CroatiaSpider(CrawlSpider):
    name = 'croatia'

    base_url = 'http://isplate.apprrr.hr/godina/'
    allowed_domains = ['isplate.apprrr.hr',]

    paginator = LinkExtractor(allow=('page', ))
    pagination_rule = Rule(paginator, callback='parse_page', follow=True)
    rules = [pagination_rule]

    def __init__(self, year=2015, *args, **kwargs):
        self.start_urls = [self.base_url + str(year)]
        super(CroatiaSpider, self).__init__(*args, **kwargs)

    def parse_page(self, response):
        self.logger.info('Landed on %s', response.url)
