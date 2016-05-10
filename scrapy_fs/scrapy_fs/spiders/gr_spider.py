import re
import urlparse
import urllib

import scrapy
from scrapy.spiders import Spider

from ..items import FarmSubsidyItem


class GRSpider(Spider):
    name = "GR"
    YEAR = 2014

    AMOUNT_RE = re.compile('^([-\d\.]+)')

    SEARCH_PAGE = 'https://transpay.opekepe.gr/welcome/search/%s'

    start_urls = [
        'https://transpay.opekepe.gr/'
    ]

    def parse(self, response):
        req = scrapy.FormRequest.from_response(response, formxpath='//form[@id="search-form"]', callback=self.search)
        csrf_token = urlparse.parse_qs(req.body)['csrf_token_'][0]
        return req.replace(body='csrf_token_=%s&firstname=&lastname=&company=&prefecture=&municipality=&regime=&year=%d&lower=-1&upper=-1&submit=1' % (csrf_token, self.YEAR))

    def search(self, response):
        limit = 500
        max_rows = int(response.xpath('//div/label[starts-with(text(), "1-11")]/text()')[0].extract().split('/')[1])
        dummy_req = scrapy.FormRequest.from_response(response, callback=self.search_page)
        csrf_token = urlparse.parse_qs(dummy_req.body)['csrf_token_'][0]

        for i in range(1, max_rows, limit):
            req = dummy_req.replace(body=urllib.urlencode({
                'csrf_token_': csrf_token,
                'limit': str(limit),
                'total_rows': str(max_rows),
                'year': str(self.YEAR),
                'lower': '-1',
                'upper': '-1',
                'submit': '1'
                }),
                url=self.SEARCH_PAGE % i)
            yield req

    def search_page(self, response):
        for tr in response.xpath('.//table/tbody/tr'):
            tds = [td.extract() for td in tr.xpath('./td/text()')]
            if 'No results' in tds[1]:
                break
            yield FarmSubsidyItem(
                year=self.YEAR,
                scheme='%s (%s)' % (tds[3], tds[4]),
                amount=float(self.AMOUNT_RE.search(tds[5]).group(1)),
                recipient_id='GR-%s-%s' % (self.YEAR, tds[0]),
                recipient_name=tds[1] if not tds[1].startswith('ANONYMOUS') else '',
                recipient_location=tds[2],
                country='GR', currency='EUR',
            )
