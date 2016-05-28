""" This is the scraper for Lithuania. """


from scrapy import Request
from scrapy.spiders.crawl import Spider


class LithuaniaSpider(Spider):
    name = 'lithuania'
    country = 'LT'
    allowed_domains = ['portal.nma.lt']
    base_url = 'https://portal.nma.lt/nma-portal/pages/fas_search'

    X_NEXT_LINK = './/a[contains(@href, "showPage") and contains(text(), "Kitas")]'
    RE_PAGE_COUNT = r'showPage\((\d+)\)'

    def __init__(self, year=2015, *args, **kwargs):
        self.year = str(year)
        self.page_count = 1
        self.query ={
            'pa': 'pl',
            'pTipas': 'p',
            'programos_kodas': 'KP13',
            'action': 'Search',
            'fin_metai': self.year,
        }
        super(LithuaniaSpider, self).__init__(*args, **kwargs)

    @property
    def pagination_url(self):
        self.query.update({'psl_nr': str(self.page_count)})
        query_string = [key + '=' + value for key, value in self.query.items()]
        return self.base_url + '?' + '&'.join(query_string)

    def start_requests(self):
        return [Request(self.pagination_url, method='POST')]

    def parse(self, response):
        self.logger.debug('Landed on %s', response.url)
        page_count = response.xpath(self.X_NEXT_LINK).re_first(self.RE_PAGE_COUNT)
        if page_count:
            self.page_count = page_count
        return Request(self.pagination_url, method='POST')
