""" This is the scraper for Lithuania. """


from scrapy import Request
from scrapy.spiders.crawl import Spider


# Translations
YEAR = 'fin_metai'
COUNTER = 'psl_nr'


class LithuaniaSpider(Spider):
    name = 'lithuania'
    country = 'LT'
    allowed_domains = ['portal.nma.lt']

    def __init__(self, year=2015):
        self.year = year
        self.page = Paginator(year)
        super(LithuaniaSpider, self).__init__()

    def start_requests(self):
        return [self.page.request]

    def parse(self, response):
        self.logger.debug('Landed on page %s', self.page.counter)

        if self.page.has_more(response):
            yield self.page.request


class Paginator(object):
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

