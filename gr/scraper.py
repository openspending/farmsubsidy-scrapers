import re

from lxml import html as html_parser

import scrapa
from scrapa.forms import get_form_data


class GRScraper(scrapa.Scraper):
    HTTP_CONCURENCY_LIMIT = 3
    QUEUE_SIZE = 0
    CONSUMER_COUNT = 3
    SESSION_POOL_SIZE = 3
    CONNECT_TIMEOUT = 90

    ENABLE_WEBSERVER = False

    BASE_URL = 'https://transpay.opekepe.gr/'

    AMOUNT_RE = re.compile('^([-\d\.]+)')
    LIMIT = 500
    NUM_PAGES = 5

    async def start(self):
        await self.schedule_many(self.get_year, range(2014, 2016))

    def get_offsets(self, max_rows):
        current = 1
        yield current
        while current <= max_rows:
            current += self.LIMIT * self.NUM_PAGES
            yield current

    async def initialize_session(self, session, year):
        response = await session.get()
        form = response.dom().xpath('//form[@id="search-form"]')[0]
        form_data = get_form_data(form)
        form_data.update({
            'lower': '-1',
            'upper': '-1',
            'year': year,
            'company': '',
            'prefecture': '',
            'municipality': '',
            'regime': '',
            'submit': '1'
        })
        response = await session.post(data=form_data)
        form_data['total_rows'] = response.xpath('.//input[@name="total_rows"]/@value')[0]
        return form_data

    @scrapa.store
    async def get_year(self, year):
        with self.get_session() as session:
            form_data = await self.initialize_session(session, year)
            total_rows = int(form_data['total_rows'])
            await self.schedule_many(self.get_pages, (((), {
                'year': year, 'offset': offset,
                'total_rows': total_rows})
                for offset in self.get_offsets(total_rows)
            ))

    @scrapa.store
    async def get_pages(self, year=None, total_rows=None, offset=None):
        with self.get_session() as session:
            form_data = await self.initialize_session(session, year)
            for num_page in range(self.NUM_PAGES):
                form_data.update({
                    'limit': str(self.LIMIT),
                })
                url_offset = offset + self.LIMIT * num_page
                if url_offset > total_rows:
                    continue
                print('Requesting offset %d' % url_offset)
                response = await session.post('/welcome/search/%s' % url_offset, data=form_data, headers={'X-Requested-With': 'XMLHttpRequest'})
                print('Got data for offset %d' % url_offset)
                dom = html_parser.fromstring(response.json())
                for tr in dom.xpath('.//table/tbody/tr'):
                    tds = [td for td in tr.xpath('./td/text()')]
                    if not len(tds):
                        print(str(tr))
                        raise ValueError
                    if 'No results' in tds[1]:
                        break
                    await self.store_result('%s-%s-%s' % (year, tds[0], tds[3]),
                        'payment', {
                            'year': year,
                            'scheme': '%s (%s)' % (tds[3], tds[4]),
                            'amount': float(self.AMOUNT_RE.search(tds[5]).group(1)),
                            'recipient_id': 'GR-%s-%s' % (year, tds[0]),
                            'recipient_name': tds[1] if not tds[1].startswith('ANONYMOUS') else '',
                            'recipient_location': tds[2],
                            'country': 'GR',
                            'currency': 'EUR',
                        })


def main():
    scraper = GRScraper()
    scraper.run_from_cli()

if __name__ == '__main__':
    main()
