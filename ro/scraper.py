from datetime import datetime
import csv
import os
import asyncio

import aiohttp
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

import scrapa
from scrapa.selenium import SeleniumMixin


class ROScraper(SeleniumMixin, scrapa.Scraper):
    BASE_URL = 'http://plati.afir.info/ListePlatiFegaFeadr.aspx'
    CONSUMER_COUNT = 1

    async def start(self):
        await self.schedule_many(self.download_year, [2014, 2015])

    async def get_first_page(self, year):
        already_page = 0
        while True:
            already_page += 1
            has_page = await self.has_result('%s-%s' % (year, already_page), 'page_data')
            if not has_page:
                break
        return already_page

    @scrapa.store
    async def download_year(self, year):
        def wait_for_load(session):
            WebDriverWait(session.driver, 90).until(
                EC.presence_of_element_located((By.XPATH, './/body[not(@class)]')))
        print('Running with', year)

        first_page = await self.get_first_page(year)
        ready = True

        if first_page != 1:
            ready = False

        with self.selenium(driver_name='phantomjs') as session:
            # session.driver.set_window_size(1132, 800)
            await session.get(self.BASE_URL)
            print('Selecting year', year)
            select = Select(session.driver.find_element_by_id("FILTER_AN_FINANCIAR"))
            select.select_by_visible_text(str(year))
            session.driver.find_element_by_id('FILTER_BUTTON').click()
            await asyncio.sleep(1)
            wait_for_load(session)
            select = Select(session.driver.find_element_by_id("FILTER_AN_FINANCIAR"))
            print('Selected year is', select.first_selected_option.text)
            print('Setting order')
            order_heading = session.find_elements_by_xpath('.//table[@id="GridView1"]//th')[1]
            print(order_heading.text)
            order_heading.el.click()
            await asyncio.sleep(2)
            wait_for_load(session)
            print('Starting on page 1')
            page_no = 1
            while True:
                dom = session.dom()
                if not ready:
                    # Find correct page link site
                    links = session.driver.find_elements_by_xpath('.//a[contains(@href, "Page$%s")]' % first_page)
                    if not links:
                        print('Could not find', first_page, 'advancing...')
                        # Fail, advance as to next pagination section
                        session.driver.find_elements_by_xpath('.//a[contains(@href, "Page$")]')[-1].click()
                    else:
                        # Success, we are ready to scrape, go to first page
                        print('Found', first_page, 'start scraping...')
                        ready = True
                        links[0].click()
                        page_no = first_page

                    wait_for_load(session)
                    continue

                print('Saving table %s' % page_no)
                await self.save_table(year, dom)
                page_no += 1
                links = session.driver.find_elements_by_xpath('.//a[contains(@href, "Page$%s")]' % page_no)
                if not links:
                    print('Found no more pagination links at', page_no)
                    break
                print('Going to page %s' % page_no)
                links[0].click()
                wait_for_load(session)

    async def save_table(self, year, dom):
        # 'Denumire beneficiar	Cod unic	Localitate	Fond	Masura	Cuantum'.split()
        COL_NAMES = ('recipient_name', 'recipient_id', 'recipient_location', 'scheme_1', 'scheme_2', 'amount')
        table = dom.xpath('//table[@id="GridView1"]')[0]
        rows = table.xpath('./tbody/tr')
        page_no = int(rows[-1].xpath('.//td/span/text()')[0])
        data = []
        for row in rows[1:-1]:
            texts = row.xpath('./td/text()')
            d = dict(zip(COL_NAMES, texts))
            d['year'] = year
            d['currency'] = 'EUR'
            d['country'] = 'RO'
            data.append(d)
        key = '%s-%s' % (year, page_no)
        await self.store_result(key, 'page_data', data)


def main():
    scraper = ROScraper()
    scraper.run_from_cli()


if __name__ == '__main__':
    main()
