import json

import scrapy
from scrapy.spiders import Spider

from ..items import FarmSubsidyItem


class ATSpider(Spider):
    name = "AT"
    YEAR = 2014
    START_URL = 'http://www.transparenzdatenbank.at/suche'
    DETAIL_URL = 'http://www.transparenzdatenbank.at/suche/details/{id}/{year}'
    DEFAULT_SEARCH = '{"name":"","betrag_von":"","betrag_bis":"","gemeinde":"","massnahme":null,"jahr":%s,"sort":"name"}' % YEAR

    def start_requests(self):
        return [scrapy.Request(self.START_URL,
                                   method='POST',
                                   headers={
                                        'PAGINATION_CURRENT': 1,
                                        'PAGINATION_PER_PAGE': 2000000
                                   },
                                   body=self.DEFAULT_SEARCH,
                                   callback=self.get_results)]

    def get_results(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html
        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        all_items = json.loads(response.body)
        for item in all_items:
            item_data = dict(
                country='AT', currency='EUR',
                year=item['jahr'],
                recipient_name=item['name'],
                recipient_id='AT-%s' % item['id'],
                recipient_location=item['gemeinde'],
                recipient_postcode=str(item['plz']),
                amount=item['betrag'],
            )
            yield scrapy.Request(self.DETAIL_URL.format(id=item['id'], year=item['jahr']),
                                       callback=self.get_detail, meta={'item_data': item_data})

    def get_detail(self, response):
        item_data = response.meta['item_data']
        all_payments = json.loads(response.body)
        for payment in all_payments:
            new_item = dict(item_data)
            new_item['amount'] = payment['betrag']
            new_item['scheme'] = u'{bezeichnung} ({id})'.format(**payment)

            yield FarmSubsidyItem(**new_item)
