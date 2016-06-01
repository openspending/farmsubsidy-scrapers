import re
import math
import os

from scrapa import Scraper, async
from scrapa.storage import DatabaseStorage
from scrapa.forms import get_form_data


class IEScraper(Scraper):

    START_URLS = {
        2014: 'https://publicapps.agriculture.gov.ie/capben/cap_ben_search_previous_year_if.jsp',
        2015: 'https://publicapps.agriculture.gov.ie/capben/loadsearch.do'
    }
    LIST_URLS = {
        2014: 'https://publicapps.agriculture.gov.ie/capben/cap_ben_results_previous_year_if.jsp?',
        2015: 'https://publicapps.agriculture.gov.ie/capben/cap_ben_results_current_year_if.jsp?',
    }
    BASE_URL = 'https://publicapps.agriculture.gov.ie'

    TERMS_URL = '/capben/cap_ben_terms.jsp'
    SEARCH_URL = '/capben/search.do'

    LOCATIONS = [
        "CARLOW", "CAVAN", "CLARE", "CORK", "DONEGAL", "DUBLIN", "GALWAY", "KERRY",
        "KILDARE", "KILKENNY", "LAOIS", "LEITRIM", "LIMERICK", "LONGFORD", "LOUTH",
        "MAYO", "MEATH", "MONAGHAN", "NORTHERN IRELAND", "OFFALY", "OUTSIDE IRELAND",
        "ROSCOMMON", "SLIGO", "TIPPERARY", "WATERFORD", "WESTMEATH", "WEXFORD", "WICKLOW",
    ]
    RESULT_COUNT_RE = re.compile('Viewing results (\d+) to (\d+) of (\d+)')
    PAGE_SIZE = 15

    @async
    def start(self):
        yield from self.schedule_many(self.prepare_search, self.generate_params())
        print('Scheduled all')

    def generate_params(self):
        for year in self.START_URLS:
            for loc in self.LOCATIONS:
                yield (year, loc), {}

    @async(store=True)
    def prepare_search(self, year, location):
        with self.get_session() as session:
            response = yield from self.perform_search(session, year, location)

        # Determine number of pages
        match = self.get_count(response)
        count = int(match.group(3))
        page_count = math.ceil(count / self.PAGE_SIZE)
        yield from self.schedule_many(self.search, ((year, location, p + 1)
                                      for p in range(page_count)))

    @async
    def perform_search(self, session, year, location):
        yield from session.get(self.TERMS_URL)
        response = yield from session.get(self.START_URLS[year])
        form = response.xpath('.//form[@name="seachForm"]')[0]
        data = get_form_data(form)
        data['location'] = location
        response = yield from session.post(self.SEARCH_URL, data=data)
        return response

    def get_count(self, response):
        text = response.xpath('.//div[@id="if_content"]')[0].text_content()
        return self.RESULT_COUNT_RE.search(text)

    @async(store=True)
    def search(self, year, location, page):
        url = self.LIST_URLS[year]
        with self.get_session() as session:
            yield from self.perform_search(session, year, location)
            response = yield from session.get(url + ('PageNo=%d' % page))
            match = self.get_count(response)
            start, end = int(match.group(1)), int(match.group(2))
            for i in range(start, end + 1):
                response = yield from session.get(url + ('RecNo=%d' % i))
                dom = response.dom()
                name = dom.xpath('.//td[text()="Name"]/following-sibling::td/text()')[0].strip()
                municipal = dom.xpath('.//td[text()="Municipal District"]/following-sibling::td/text()')[0].strip()
                key = '%s@%s@%s@%s' % (name, location, municipal, year)
                yield from self.store_result(key, 'recipient', {
                    'name': name,
                    'year': year,
                    'municipal': municipal,
                    'location': location,
                    'amounts': list(self.get_amounts(dom))
                })

    def get_amounts(self, dom):
        for tr in dom.xpath('(//table//table)[2]//tr[position() > 1]'):
            scheme_amount = tr.xpath('.//td/text()')
            if len(scheme_amount) != 2:
                continue
            scheme, amount = scheme_amount
            amount = float(amount.replace('€', '').replace(',', ''))
            yield scheme, amount


def main():
    path = os.path.join(os.getcwd(), 'ie_data.db'),
    db_url = 'sqlite:///%s' % path
    scraper = IEScraper(storage=DatabaseStorage(db_url=db_url))
    scraper.run_from_cli()


if __name__ == '__main__':
    main()
