import json

import scrapy
from scrapy.spiders import Spider
# from scrapy.shell import inspect_response

from ..items import FarmSubsidyItem


class ATSpider(Spider):
    name = "AT"
    YEAR = 2017
    START_URL = 'https://www.transparenzdatenbank.at/suche'
    DETAIL_URL = 'https://www.transparenzdatenbank.at/suche/details/{id}/{year}'
    DEFAULT_SEARCH = u'{"name":"","betrag_von":"","betrag_bis":"","gemeinde":"","massnahme":null,"jahr":%s,"sort":"name"}' % YEAR

    def __init__(self, year=YEAR):
        self.year = int(year)

    def start_requests(self):
        # import ipdb; ipdb.set_trace()
        yield scrapy.Request(self.START_URL,
               method='POST',
               headers={
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Accept': 'application/json, text/plain, */*',
                    'PAGINATION_CURRENT': 1,
                    'PAGINATION_PER_PAGE': 2000000,
                    'Referer': 'https://www.transparenzdatenbank.at/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
               },
               body=self.DEFAULT_SEARCH,
               callback=self.get_results)

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
