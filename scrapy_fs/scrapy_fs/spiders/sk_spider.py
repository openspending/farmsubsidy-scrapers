import re

import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


class SKSpider(Spider):
    name = "SK"
    NUM_ONLY_RE = re.compile('^[\s\d]+$')

    def __init__(self, year=None):
        self.year = int(year)

    def start_requests(self):
        self.SEARCH_URL = 'http://www.apa.sk/index.php?offset=%s&navID=511&euod=&eudo=&order=&rok=' + str(self.year)
        url = self.SEARCH_URL % '1'
        yield scrapy.Request(url)

    def parse(self, response):
        max_page = response.xpath('.//div[@id = "strankovanie"]//div')[0].extract()
        match = re.search(r'\(\d+/(\d+)\)', max_page)
        max_page = int(match.group(1))
        print('Max pages', max_page)
        for x in self.search_page(response):
            yield x

        for i in range(2, max_page + 1):
            yield scrapy.Request(self.SEARCH_URL % i)

    def search_page(self, response):
        trs = response.xpath('.//table//tr')
        for i, tr in enumerate(trs):
            if i == 0:
                continue
            tds = [x.extract() for x in tr.xpath('./td//text()')]
            scheme = tds[3].strip()
            year = int(tds[5].strip())
            amount = float(tds[4])
            recipient_postcode = tds[1].strip()
            recipient_location = tds[2].strip()
            recipient_name = tds[0]
            if recipient_name.startswith('B20'):
                recipient_id = u'SK-%s' % recipient_name
                recipient_name = ''
            else:
                recipient_id = u'SK-%s-%s' % (recipient_postcode, slugify(recipient_name))

            yield FarmSubsidyItem(
                year=year,
                scheme=scheme,
                amount=amount,
                recipient_id=recipient_id,
                recipient_name=recipient_name,
                recipient_location=recipient_location,
                recipient_postcode=recipient_postcode,
                country='SK', currency='EUR',
            )
