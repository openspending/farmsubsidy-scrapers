import re

import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


class SKSpider(Spider):
    name = "SK"
    NUM_ONLY_RE = re.compile('^[\s\d]+$')

    SEARCH_URL = 'http://www.apa.sk/index.php?offset=%s&navID=511&euod=&eudo=&order='
    start_urls = [
        SEARCH_URL % '1'
    ]

    def parse(self, response):
        max_page = response.xpath('.//div[@id = "strankovanie"]//a[last()]/@href')[0].extract()
        max_page = int(max_page.split('offset=')[1].split('&')[0])
        for x in self.search_page(response):
            yield x

        for i in range(2, max_page + 1):
            yield scrapy.Request(self.SEARCH_URL % i)

    def search_page(self, response):
        trs = response.xpath('.//div[@class="row-disabled"]//table//tr')
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
