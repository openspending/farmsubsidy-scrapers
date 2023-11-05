import json
import string

import scrapy
from scrapy.spiders import Spider
# from scrapy.shell import inspect_response

from ..items import FarmSubsidyItem


class DESpider(Spider):
    name = "DE"
    _YEAR = 2018
    YEAR = 'jahr'
    START_URL = 'https://agrar-fischerei-zahlungen.de/Suche'

    def __init__(self):
        pass

    def get_plzs(self):
        for i in range(0, 100000):
            yield str(i).zfill(5) + '%'
        for i in range(0, 10000):
            yield str(i).zfill(4)
        for l in string.ascii_letters:
            yield '%' + l + '%'

    def start_requests(self):
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

    def search(self, plz):
        page = 1
        per_page = 50
        count, count_beg = 1000, 1000
        while True:
            offset = str(per_page * (page - 1))
            if page == 1:
                response = requests.post(BASE_URL, data={
                    'jahr': YEAR,
                    'name': '',
                    'plz': plz,
                    'ort': '',
                    'suchtypBetrag': 'betrag_massnahme',
                    'operator': 'eq',
                    'betrag': '',
                    'suchtypEgfl': 'egfl_alle'
                })

                text = response.text
                if 'Es liegen mehr als 1500 Ergebnisse vor' in text:
                    raise ValueError('Search %s result in too many!' % plz)

                dom = html.fromstring(text)
                form_data = get_form_data(dom.xpath('.//form[@id="data"]')[0])
                if 'count' not in form_data:
                    # No results
                    return None
                count = form_data['count']
                count_beg = form_data['countBeg']

            response = requests.post(BASE_URL, data={
                'jahr': YEAR,
                'name': '',
                'ort': '',
                'plz': plz,
                'suchtypBetrag': 'betrag_massnahme',
                'operator': 'eq',
                'betrag': '',
                'suchtypEgfl': 'egfl_alle',
                'suchtypEler': 'eler_alle',
                'viewOffset': str(offset),
                'viewOrderdir': 'asc',
                'viewOrderby': 'zahlungsempfaenger',
                'viewCount': str(count),
                'viewCountBeg': str(count_beg),
                'viewLimit': str(per_page),
                'offset': str(offset),
                'dir': 'asc',
                'order': 'zahlungsempfaenger',
                'count': str(count),
                'countBeg': str(count_beg),
                'prevLimit': str(per_page),
                'limit': str(per_page),
                'seite': str(page)
            })
            dom = html.fromstring(response.text)
            buttons = dom.xpath('.//button[@name="showBeg"]')
            for x in buttons:
                detail_queue.put((x.attrib['value'], plz, page))
            nav_text = dom.xpath('.//div[@id="listNavRight"]')[0].text_content()
            nav_text = nav_text.strip() + '|'
    #         print('%s lines for %s - now on page %d' % (count_beg, plz, page))
            if 'von %d|' % page in nav_text:
                break
            page += 1
    #         print('Going to page %d of %s' % (page, plz))

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
