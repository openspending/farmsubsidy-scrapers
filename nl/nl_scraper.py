import asyncio
import math
import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

import scrapa
from scrapa.selenium import SeleniumMixin


class NLScraper(SeleniumMixin, scrapa.Scraper):
    BASE_URL = 'https://mijn.rvo.nl/web/klantportaal-site/'
    CONSUMER_COUNT = 1
    ENABLE_WEBSERVER = False

    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.113 Safari/537.36'

    TOTAL_RE = re.compile('\d+-\d+ van (\d+) resultaten')
    POST_REST_RE = re.compile('\s*([\w-]+)\s+(.*)')
    AMOUNT_RE = re.compile('([\d\.]+,\d+)')

    YEARS = [2014, 2015]

    REGIONS = (
        'Buiten Nederland',
        'Drenthe',
        'Flevoland',
        'Friesland',
        'Gelderland',
        'Groningen',
        'Limburg',
        'Noord-Brabant',
        'Noord-Holland',
        'Overijssel',
        'Utrecht',
        'Zeeland',
        'Zuid-Holland',
    )

    async def start(self):
        await self.schedule_many(self.download_year_region, (
            (x, {}) for x in self.get_combinations()
        ))

    def get_combinations(self):
        for year in self.YEARS:
            for region in self.REGIONS:
                yield year, region

    async def get_first_page(self, year, region):
        already_page = 0
        while True:
            already_page += 1
            has_page = await self.has_result('%s-%s-%s' % (year, region, already_page), 'page_data')
            if not has_page:
                break
        return already_page

    @scrapa.store
    async def download_year_region(self, year, region):
        def wait_for_load(session):
            WebDriverWait(session.driver, 90).until(
                # Wait for spinner to disappear
                EC.invisibility_of_element_located((By.XPATH, './/div[@id="_EuSubsidies_WAR_EuSubsidiesportlet_:subsidiesForm:j_idt106"]')))
        print('Running with', year, region)

        first_page = await self.get_first_page(year, region)
        ready = True

        if first_page != 1:
            ready = False

        with self.selenium(driver_name='phantomjs') as session:
            session.driver.set_window_size(1250, 800)
            await session.get(self.BASE_URL + 'europese-subsidies-%s' % year)
            print('Selecting year', year)
            type_select = Select(session.driver.find_element_by_id("_EuSubsidies_WAR_EuSubsidiesportlet_:subsidiesForm:subsidie"))
            type_select.select_by_visible_text('Gemeenschappelijk Landbouw Beleid')
            region_select = Select(session.driver.find_element_by_id("_EuSubsidies_WAR_EuSubsidiesportlet_:subsidiesForm:provincie"))
            region_select.select_by_visible_text(region)
            session.driver.find_element_by_id('_EuSubsidies_WAR_EuSubsidiesportlet_:subsidiesForm:searchButton').click()
            count_select = Select(session.driver.find_element_by_id("_EuSubsidies_WAR_EuSubsidiesportlet_:subsidiesForm:glbTable_rppDD"))
            count_select.select_by_visible_text('100')
            wait_for_load(session)
            total = session.dom().xpath('//span[@class="ui-paginator-current"]/text()')[0]
            total = int(self.TOTAL_RE.match(total).group(1))
            print('Starting on page 1 (total items %d)' % total)
            total_pages = math.ceil(total / 100)
            print('expecting %d pages' % total_pages)
            page_no = 1

            while True:
                try:
                    dom = session.dom()
                    # if not ready:
                    #     # Find correct page link site
                    #
                    #     current_page = int(dom.xpath('.//span[@class="ui-paginator-page ui-state-default ui-corner-all ui-state-active"]/text()')[0])
                    #     if current_page == first_page:
                    #         ready = True
                    #     else:
                    #         available_page_nos = session.driver.find_elements_by_xpath('.//span[@class="ui-paginator-pages"]/span')
                    #         available_page_nos = [int(a.text) for a in available_page_nos]
                    #         if first_page not in available_page_nos:
                    #             print('Could not find', first_page, 'advancing...')
                    #             # Fail, advance as to next pagination section
                    #             last_links = session.driver.find_elements_by_xpath('.//span[@class="ui-paginator-pages"]/span')
                    #             last_links[-1].click()
                    #         else:
                    #             # Success, we are ready to scrape, go to first page
                    #             print('Go to', first_page, 'start scraping...')
                    #             ready = True
                    #             available_page = session.driver.find_elements_by_xpath('.//span[@class="ui-paginator-pages"]/span[text() = "%d"]' % first_page)
                    #             available_page[0].click()
                    #             page_no = first_page
                    #
                    #         wait_for_load(session)
                    #         continue

                    print('Saving table %s' % page_no)
                    await self.save_table(year, region, dom)
                    page_no += 1
                    next_links = session.driver.find_elements_by_xpath('.//span[@class="ui-paginator-next ui-state-default ui-corner-all"]')
                    if not next_links:
                        print('Found no more pagination links at', page_no, year, region)
                        break
                    print('Going to page %s' % page_no)
                    next_links[0].click()
                    wait_for_load(session)
                except Exception as e:
                    print(e)
                    raise e
                    # await asyncio.sleep(2)

    async def save_table(self, year, region, dom):
        dataset = []
        rows = dom.xpath('//tbody/tr')
        page_no = int(dom.xpath('.//span[@class="ui-paginator-page ui-state-default ui-corner-all ui-state-active"]/text()')[0])
        for row in rows:
            name_col, scheme_col, amount_col = row.xpath('.//td')
            parts = name_col.xpath('.//li/text()')
            name = parts[0].strip()
            name_addition = ''
            if len(parts) == 3:
                if parts[1].startswith('('):
                    name_addition = parts[1].replace('(', '').replace(')').strip()
                    name_addition = ' ' + name_addition

            postcode_location = parts[-1].strip().split(' ', 1)
            postcode = None
            if len(postcode_location) == 2:
                postcode = postcode_location[0]
                location = postcode_location[1]
            else:
                location = postcode_location[0]

            scheme = scheme_col.xpath('.//text()')[0].strip()
            amount = amount_col.xpath('.//span/text()')[0].strip()
            amount = float(self.AMOUNT_RE.search(amount).group(1).replace('.', '').replace(',', '.'))
            data = {
                'recipient_name': name + name_addition,
                'recipient_postcode': postcode,
                'recipient_location': location,
                'scheme': scheme,
                'amount': amount,
                'currency': 'EUR',
                'country': 'NL',
                'year': year,
            }
            data['recipient_id'] = 'NL-{recipient_postcode}-{recipient_name}-{recipient_location}'.format(**data)
            dataset.append(data)

        key = '%s-%s-%s' % (year, region, page_no)
        await self.store_result(key, 'page_data', dataset)


def main():
    scraper = NLScraper()
    scraper.run_from_cli()


if __name__ == '__main__':
    main()
