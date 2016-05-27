""" This is the scraper for Lithuania. """


from scrapy.spiders import CrawlSpider
from scrapy import FormRequest
from scrapy.utils.response import open_in_browser


class LithuaniaSpider(CrawlSpider):
    name = 'lithuania'
    country = 'LT'

    SEARCH_URL = 'https://portal.nma.lt/nma-portal/pages/fas_search'
    SEARCH_QUERY = {
        'pa': 'pl',
        'pTipas': 'p',
        'psl_nr': '1',
        'programos_kodas': 'KP13',
        'fin_metai': '2014',
        'action': 'Search'
    }

    def __init__(self, year=2015, *args, **kwargs):
        self.year = year
        super(LithuaniaSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        self.SEARCH_QUERY.update({'fin_metai': str(self.year)})
        return [FormRequest(self.SEARCH_URL, formdata=self.SEARCH_QUERY)]

    def parse(self, response):
        open_in_browser(response)
