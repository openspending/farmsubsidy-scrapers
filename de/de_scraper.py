from collections import defaultdict
import os

from scrapa import Scraper, async
from scrapa.forms import get_form_data
from scrapa.storage import DatabaseStorage


def parse_amount(amount):
    ''' 1,045,093.56 €'''
    amount = amount.replace('€', '')
    amount = amount.strip()
    if amount[-3] == ',':
        amount = amount.replace('.', '')
        amount = amount.replace(',', '.')
    elif amount[-3] == '.':
        amount = amount.replace(',', '')
    return float(amount)


class DEScraper(Scraper):
    BASE_URL = 'http://agrar-fischerei-zahlungen.de/afig/Suche'

    @async
    def start(self):
        yield from self.schedule_many(self.search, self.get_plzs())
        print('Done adding all PLZ searches')

    def get_plzs(self):
        with open('plz.txt') as f:
            for line in f:
                plz = line.strip()
                if plz:
                    yield plz

    @async(store=True)
    def search(self, plz):
        page = 1
        per_page = 50
        count, count_beg = 1000, 1000
        while True:
            offset = str(per_page * (page - 1))
            if page == 1:
                response = yield from self.post(data={
                    'jahr': 'jahr',
                    'name': '',
                    'plz': plz,
                    'ort': '',
                    'suchtypBetrag': 'betrag_massnahme',
                    'operator': 'eq',
                    'betrag': '',
                    'suchtypEgfl': 'egfl_alle'
                })
                dom = response.dom()
                form_data = get_form_data(dom.xpath('.//form[@id="data"]')[0])
                if 'count' not in form_data:
                    # No results
                    return None
                count = form_data['count']
                count_beg = form_data['countBeg']

            response = yield from self.post(data={
                'jahr': 'jahr',
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
            dom = response.dom()
            buttons = dom.xpath('.//button[@name="showBeg"]')
            button_values = [x.attrib['value'] for x in buttons]
            yield from self.schedule_many(self.detail, button_values)
            nav_text = dom.xpath('.//div[@id="listNavRight"]')[0].text_content()
            print('%s lines for %s - now on page %d' % (count, plz, page))
            if 'von %d' % page in nav_text:
                break
            page += 1
            print('Going to page %d of %s' % (page, plz))

    @async(store=True)
    def detail(self, uuid):
        response = yield from self.post(data={
            'suchtypBetrag': 'betrag_massnahme',
            'operator': 'eq',
            'betrag': '',
            'suchtypEgfl': 'egfl_alle',
            'suchtypEler': 'eler_alle',
            'showBeg': uuid
        })
        dom = response.dom()
        jahr = int(dom.xpath('.//h1[@id="titel"]')[0].text.strip().split(' ')[-1])
        h2 = dom.xpath('.//div[@id="beguenstigter"]//h2')[0].text
        h3s = dom.xpath('.//div[@id="beguenstigter"]//h3')
        amounts = dom.xpath('.//div[@id="beguenstigter"]//span[@class="betrag"]')
        result = defaultdict(list)
        for massnahme, amount in zip(h3s, amounts):
            amount = parse_amount(amount.text)
            result[massnahme.text_content().strip()].append(amount)
        total = parse_amount(amounts[-2].text)
        name, location = h2.rsplit(' – ', 1)
        plz, location = location.split(' ', 1)
        yield from self.store_result(uuid, 'recipient', {
            'jahr': jahr,
            'name': name,
            'plz': plz,
            'location': location,
            'total': total,
            'schemes': result
        })


def main():
    path = os.path.join(os.getcwd(), 'de_data.db'),
    db_url = 'sqlite:///%s' % path
    scraper = DEScraper(storage=DatabaseStorage(db_url=db_url))
    scraper.run_from_cli()


if __name__ == '__main__':
    main()
