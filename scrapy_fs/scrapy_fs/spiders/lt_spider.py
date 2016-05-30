""" This is the scraper for Lithuania. """


from UserList import UserList
from scrapy import Request
from scrapy.spiders.crawl import Spider
from scrapy.selector import Selector

from scrapy_fs.items import LithuanianLoader, FarmSubsidyItem


class LithuaniaSpider(Spider):
    name = 'lithuania'
    country = 'LT'
    allowed_domains = ['portal.nma.lt']

    AGENCY_COLUMNS = {'EADS': 5, 'EAFRD': 7}

    X_MUNICIPALITY = './td[2]/text()'
    X_DISTRICT = './td[3]/text()'
    X_SCHEME = './td[4]/text()'

    def __init__(self, year=2015):
        self.year = int(year)
        self.page = TablePaginator(year)
        super(LithuaniaSpider, self).__init__()

    def start_requests(self):
        return [self.page.request]

    def parse(self, response):
        self.logger.debug('Landed on page %s', self.page.counter)

        recipients = Recipients(response)
        self.logger.debug('Found %s recipients', len(recipients))

        for id_, name, subsidies in recipients:
            for row in subsidies:
                for agency, column in self.AGENCY_COLUMNS.items():
                    subsidy = LithuanianLoader(item=FarmSubsidyItem(), selector=row)
                    x_amount = self.build_amount_xpath(column)

                    subsidy.add_value('currency', 'EUR')
                    subsidy.add_value('country', self.country)
                    subsidy.add_xpath('scheme', self.X_SCHEME)
                    subsidy.add_value('agency', agency)
                    subsidy.add_xpath('amount', x_amount)
                    subsidy.add_value('recipient_id', id_)
                    subsidy.add_value('recipient_name', name)
                    subsidy.add_xpath('recipient_location', self.X_MUNICIPALITY)
                    subsidy.add_xpath('recipient_location', self.X_DISTRICT)

                    subsidy.load_item()
                    self.logger.debug('Loaded %s', dict(subsidy.item))
                    yield subsidy.item

            self.logger.debug('Parsed subsidies for %s', name)

        if self.page.has_more(response):
            yield self.page.request
        else:
            self.logger.debug('Pagination complete')

    def build_amount_xpath(self, column):
        # Tables for 2013 & 2014 have subsidies in both LTL and EUR.
        xpath = './td[%s]/text()' if self.year == 2015 else './td[%s]/table/tr[2]/td[1]/text()'
        return xpath % column


class Recipients(UserList):
    X_IS_HEADER = r'id="N(\w{5})"'
    X_ROWS = '//table[@class="table"][1]/tr'
    X_RECIPIENT_IDS = '//table[@class="table"]/tr[contains(@id, "N")]/@id'
    X_RECIPIENT_NAMES = '//table[@class="table"]/tr[contains(@id, "N")]/td[1]/a/text()'

    def __init__(self, response):
        document = Selector(response)
        self.rows = document.xpath(self.X_ROWS)

        ids = map(self.extract, document.xpath(self.X_RECIPIENT_IDS))
        names = map(self.extract, document.xpath(self.X_RECIPIENT_NAMES))
        subsidies = self.collect_subsidies()

        recipients = zip(ids, names, subsidies)
        super(Recipients, self).__init__(recipients)

    def collect_subsidies(self):
        i_recipients = list(self.recipient_indices)
        for i, i_recipient in enumerate(i_recipients):
            if i_recipient != i_recipients[-1]:
                next_i_recipient = i_recipients[i + 1]
            else:
                next_i_recipient = -1
            yield self.rows[i_recipient + 1:next_i_recipient]

    @property
    def recipient_indices(self):
        for i, row in enumerate(self.rows):
            if row.re(self.X_IS_HEADER):
                yield i

    @staticmethod
    def extract(selector):
        return selector.extract()


# Translations
YEAR = 'fin_metai'
COUNTER = 'psl_nr'


class TablePaginator(object):
    base_url = 'https://portal.nma.lt/nma-portal/pages/fas_search'
    query = {
        'pa': 'pl',
        'pTipas': 'p',
        'programos_kodas':
        'KP13', 'action':
        'Search',
        'psl_nr': '1',
        'fin_metai': '2015'
    }

    X_LINK = './/a[contains(@href, "showPage") and contains(text(), "Kitas")]'
    RE_COUNTER = r'showPage\((\d+)\)'

    def __init__(self, year):
        self.update(YEAR, year)

    def update(self, key, value):
        self.query.update({key: str(value)})

    def has_more(self, response):
        more = response.xpath(self.X_LINK).re_first(self.RE_COUNTER)
        self.update(COUNTER, more)
        return True if more else False

    @property
    def request(self):
        parameters = [key + '=' + value for key, value in self.query.items()]
        url = self.base_url + '?' + '&'.join(parameters)
        return Request(url, method='POST')

    @property
    def counter(self):
        return self.query[COUNTER]
