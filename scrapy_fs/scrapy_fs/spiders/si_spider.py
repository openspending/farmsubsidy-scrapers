import re

import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


class SISpider(Spider):
    name = "SI"
    NUM_ONLY_RE = re.compile('^[\s\d]+$')

    def __init__(self, year=None):
        self.year = int(year)

    def start_requests(self):
        url = 'http://pregled.arsktrp.gov.si/prejemniki%s.php' % str(self.year)[2:]
        yield scrapy.Request(url)

    def parse(self, response):
        option_list = [x.extract() for x in response.xpath('.//select[@name = "obcina"]/option/@value')]
        option_list = option_list[1:]
        for o in option_list:
            yield scrapy.FormRequest.from_response(response, formdata={
                    'obcina': o.encode('utf-8'),
                    'zadetkov': u'1000000'
            }, callback=self.search_page)

    def search_page(self, response):
        trs = response.xpath('.//table/tbody/tr')
        for tr in trs:
            tds = [x.extract() for x in tr.xpath('./td/text()')]
            scheme = tds[3].strip()
            if 'Sum total' in scheme:
                continue
            amount = float(tds[4].replace('.', '').replace(',', '.'))
            recipient_name = tds[0]
            if self.NUM_ONLY_RE.match(recipient_name) is not None:
                recipient_id = u'SI-%s-%s' % (self.year, recipient_name)
                recipient_name = ''
            else:
                recipient_id = u'SI-%s-%s' % (slugify(tds[1]), slugify(recipient_name))

            recipient_location = u'%s, %s' % (tds[1], tds[2])
            yield FarmSubsidyItem(
                year=self.year,
                scheme=scheme,
                amount=amount,
                recipient_id=recipient_id,
                recipient_name=recipient_name,
                recipient_location=recipient_location,
                country='SI', currency='EUR',
            )
