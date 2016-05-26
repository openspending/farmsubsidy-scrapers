""" This is the scraper for Croatia. """

from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from copy import deepcopy

from scrapy_fs.items import CroatiaItemLoader, FarmSubsidyItem


class CroatiaSpider(CrawlSpider):
    name = 'croatia'

    paginator = LinkExtractor(allow=('page', ))
    pagination_rule = Rule(paginator, callback='parse_table', follow=True)
    allowed_domains = ['isplate.apprrr.hr']
    rules = [pagination_rule]

    start_url_format = 'http://isplate.apprrr.hr/godina/%s'
    details_url_format = start_url_format + '/korisnik/%s'

    X_TABLE = '//tbody'
    X_ROWS = './/tr'

    X_REFERENCE = './/td[1]/text()'
    X_DETAILS_URL = './/td[@scope="row"]/a/@href'

    X_NAME = '//div[@class="well"]/ul/li[1]/text()'
    X_ID = '//div[@class="well"]/ul/li[2]/text()'
    X_CITY = '//div[@class="well"]/ul/li[3]/text()'
    X_REGION = '//div[@class="well"]/ul/li[4]/text()'

    X_AGENCY = './/td[1]/text()'
    X_SCHEME = './/td[2]/text()'
    X_YEAR = './/td[3]/text()'
    X_AMOUNT = './/td[5]/text()'

    IGNORE_SUM = slice(0, -1)

    def __init__(self, year=2015, *args, **kwargs):
        self.year = str(year)
        self.start_urls = [self.start_url_format % self.year]
        super(CroatiaSpider, self).__init__(*args, **kwargs)

    def parse_recipients(self, response):
        """ Parse the main (paginated) table where the recipients are listed.

        @url        http://isplate.apprrr.hr/godina/2015
        @returns    requests 101

        """
        self.logger.info('Landed on %s', response.url)

        table = response.xpath(self.X_TABLE)
        rows = table.xpath(self.X_ROWS)

        for row in rows:
            reference = row.xpath(self.X_REFERENCE).extract_first()
            details_url = self.details_url_format % (self.year, reference)
            yield Request(details_url, callback=self.parse_subsidies)

    def parse_subsidies(self, response):
        """ Parse information on the recipient page.

        1. The recipient information above the subsidy table
        2. Each row in the subsidy table

        @url        http://isplate.apprrr.hr/godina/2015/korisnik/201095

        @scrapes    recipient_name
        @scrapes    recipient_id
        @scrapes    recipient_address
        @scrapes    recipient_location
        @scrapes    agency
        @scrapes    scheme
        @scrapes    year
        @scrapes    amount

        """
        self.logger.debug('Landed on recipient page %s', response.url)

        table = response.xpath(self.X_TABLE)
        rows = table.xpath(self.X_ROWS)[self.IGNORE_SUM]

        for row in rows:
            recipient = CroatiaItemLoader(item=FarmSubsidyItem(), response=response)

            recipient.add_xpath('recipient_name', self.X_NAME)
            recipient.add_xpath('recipient_id', self.X_ID)
            recipient.add_xpath('recipient_location', self.X_CITY)
            recipient.add_xpath('recipient_address', self.X_CITY)
            recipient.add_xpath('recipient_address', self.X_REGION)

            yield self._parse_subsidy(row, recipient)

    def _parse_subsidy(self, row, item):
        """ Parse each line in the recipient table as a separate subsidy item. """

        agency = row.xpath(self.X_AGENCY).extract()
        scheme = row.xpath(self.X_SCHEME).extract()
        year = row.xpath(self.X_YEAR).extract()
        amount = row.xpath(self.X_AMOUNT).extract()

        item.add_value('agency', agency)
        item.add_value('scheme', scheme)
        item.add_value('year', year)
        item.add_value('amount', amount)

        subsidy = item.load_item()
        self.logger.debug('Parsed %s subsidy from %s', subsidy['amount'], subsidy['agency'])
        return subsidy
