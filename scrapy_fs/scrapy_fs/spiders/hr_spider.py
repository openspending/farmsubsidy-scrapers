""" This is the scraper for Croatia. """

from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.shell import inspect_response

from scrapy_fs.items import CroatiaItemLoader, FarmSubsidyItem


class CroatiaSpider(CrawlSpider):
    name = 'croatia'

    paginator = LinkExtractor(allow=('page', ))
    pagination_rule = Rule(paginator, callback='parse_table', follow=True)
    allowed_domains = ['isplate.apprrr.hr']
    rules = [pagination_rule]

    start_url_format = 'http://isplate.apprrr.hr/godina/%s'
    details_url_format = start_url_format + '/korisnik/%s'

    X_TABLE = r'//tbody'
    X_ROWS = r'.//tr'
    X_REFERENCE = r'.//td[1]/text()'
    X_CITY = r'.//td[3]/text()'
    X_REGION = r'.//td[4]/text()'
    X_COMPANY = r'.//td[@scope="row"]/a/text()'
    X_DETAILS_URL = r'.//td[@scope="row"]/a/@href'

    def __init__(self, year=2015, *args, **kwargs):
        self.year = str(year)
        self.start_urls = [self.start_url_format % self.year]
        super(CroatiaSpider, self).__init__(*args, **kwargs)

    def parse_table(self, response):
        """ Parse the paginated table where the companies are listed.

        @url http://isplate.apprrr.hr/godina/2015

        @returns requests 101

        @scrapes recipient_id
        @scrapes recipient_name
        @scrapes recipient_address
        @scrapes year

        """

        self.logger.info('Landed on %s', response.url)
        table = response.xpath(self.X_TABLE)

        for row in table.xpath(self.X_ROWS):
            reference = row.xpath(self.X_REFERENCE).extract_first()
            item = CroatiaItemLoader(selector=row, item=FarmSubsidyItem())

            item.add_value('recipient_id', reference)
            item.add_xpath('recipient_name', self.X_COMPANY)
            item.add_xpath('recipient_address', self.X_CITY)
            item.add_xpath('recipient_address', self.X_REGION)
            item.add_value('year', self.year)

            yield Request(
                self.details_url_format % (self.year, reference),
                callback=self.parse_details,
                meta={'loader': item}
            )

    def parse_details(self, response):
        """ Parse the page with the subsidy details. """

        self.logger.debug('Grabbing details on %s', response.url)
        item = response.meta['loader']
        return item.load()
