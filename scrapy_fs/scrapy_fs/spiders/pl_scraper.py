# -*- encoding: utf-8 -*-
import re
import math

import scrapy
from scrapy.spiders import Spider

from ..items import FarmSubsidyItem


class PLSpider(Spider):
    name = "PL"
    YEAR = 2014
    LIMIT = 50
    NUM_ONLY_RE = re.compile('^[\s\d]+$')

    SEARCH_URL = 'http://beneficjenciwpr.minrol.gov.pl/search/index/page:{page}/year:{year}/limit:{limit}'

    start_urls = [
        SEARCH_URL.format(page=1, year=YEAR, limit=LIMIT)
    ]

    def parse(self, response):

        if '/outrecords/privateacc' in response.url:
            # accept terms
            yield scrapy.FormRequest.from_response(response,
                formxpath='.//div[@class="privacy"]//form',
                formdata={
                    'data[Outrecord][accept]': '1'
                }, callback=self.parse)
            return
        max_items = int(response.css('.search_quotes').re('znaleziono: (\d+) beneficjent')[0])
        max_pages = int(math.ceil(max_items / float(self.LIMIT)))
        for x in self.search(response):
            yield x
        for page in range(2, max_pages + 1):
            yield scrapy.Request(self.SEARCH_URL.format(page=page,
                                  year=self.YEAR, limit=self.LIMIT), callback=self.search)

    def search(self, response):
        url = response.xpath('//table[@class="search_res"]//tr/td/a/@href')[0].extract()
        url = response.urljoin(url)
        yield scrapy.Request(url, callback=self.detail)

    def detail(self, response):
        recipient_url = response.url
        url_id = recipient_url.rsplit('/')[-1]

        keys = [x.extract().strip() for x in response.xpath('//div[@class="outrecord_label"]//text()')]
        values = [x for x in response.xpath('//div[@class="outrecord_data"]')]
        values = [v.xpath('.//text()')[0].extract() if v.xpath('.//text()') else '' for v in values]
        data = dict(zip(keys, values))
        year = int(data[u'Rok budżetowy'])
        recipient_name = [
            data[u'Imię beneficjenta'], data[u'Nazwisko beneficjenta'],
            data[u'Nazwa beneficjenta']
        ]
        recipient_name = ' '.join(x.strip() for x in recipient_name if x.strip())
        recipient_postcode = data[u'Kod pocztowy']
        recipient_location = data[u'Nazwa gminy']
        recipient_id = 'PL-%s-%s' % (year, url_id)

        for line in response.xpath('.//div[@class="outrecord_left_green"]/div'):
            amount = line.xpath('.//div[@class="outrecord_data_green"]//text()')[0].extract()
            amount = float(amount.replace(' ', '').replace(',', '.'))
            if not amount:
                continue
            scheme = line.xpath('.//div[@class="outrecord_label_green"]//text()')[0].extract()
            yield FarmSubsidyItem(
                year=year,
                scheme=scheme,
                amount=amount,
                recipient_id=recipient_id,
                recipient_name=recipient_name,
                recipient_location=recipient_location,
                recipient_url=recipient_url,
                recipient_postcode=recipient_postcode,
                country='PL', currency='PLN',
            )
