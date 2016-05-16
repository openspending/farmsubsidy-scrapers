# -*- encoding: utf-8 -*-
import sys

from slugify import slugify
import unicodecsv

from selenium.webdriver import PhantomJS
from selenium.webdriver.support.wait import WebDriverWait


START_URL = 'https://mijn.rvo.nl/europese-subsidies-{year}'
TIMEOUT = 3


class NLScraper(object):
    CAP_TEXT = 'Gemeenschappelijk Landbouw Beleid'

    def __init__(self, driver, **kwargs):
        self.kwargs = kwargs
        self.driver = driver
        self.driver.implicitly_wait(3)

    def wait_for_id(self, el_id):
        WebDriverWait(self.driver, TIMEOUT).until(
            lambda driver: driver.find_element_by_id(el_id).is_displayed()
        )

    def wait_for_pageload(self):
        WebDriverWait(self.driver, TIMEOUT).until(
            lambda driver: not driver.find_element_by_id('A0306:subsidiesForm:j_idt102').is_displayed()
        )

    def start(self, writer):
        self.driver.get(START_URL.format(year=self.kwargs['year']))
        self.driver.find_element_by_xpath("//select[@id='A0306:subsidiesForm:subsidie']/option[text()='%s']" % self.CAP_TEXT).click()
        self.driver.find_element_by_id('A0306:subsidiesForm:searchButton').click()
        limit_id = 'A0306:subsidiesForm:glbTable_rppDD'
        self.wait_for_id(limit_id)
        self.driver.find_element_by_xpath("//select[@id='%s']/option[text()='%s']" % (limit_id, '100')).click()
        self.wait_for_pageload()
        next_link = True
        while next_link:
            page_no = self.driver.find_element_by_xpath('.//span[@class = "ui-paginator-page ui-state-default ui-corner-all ui-state-active"]').text
            print(page_no)
            writer.writerows(list(self.scrape_table()))
            next_link = self.driver.find_elements_by_xpath('.//span[@class = "ui-paginator-next ui-state-default ui-corner-all"]')
            if next_link:
                next_link = next_link[0]
                next_link.click()
                self.wait_for_pageload()

    def scrape_table(self):
        trs = self.driver.find_elements_by_xpath('.//div[@class="ui-datatable-tablewrapper"]/table/tbody/tr')
        for tr in trs:
            tds = tr.find_elements_by_xpath('.//td')
            tds = [t.text for t in tds]
            lis = tr.find_elements_by_xpath('.//td[1]/ul/li')
            recipient_name = lis[0].text.strip()
            address = lis[1].text.strip()
            recipient_postcode, recipient_location = address.split(' ', 1)
            recipient_id = 'NL-%s-%s' % (recipient_postcode, slugify(recipient_name))
            scheme = tds[1]
            amount = tds[2]
            amount = amount.replace(u'€', '').strip().replace('.', '')
            amount = float(amount.replace(',', '.'))
            yield {
                'amount': amount,
                'scheme': scheme,
                'year': self.kwargs['year'],
                'country': 'NL',
                'currency': 'EUR',
                'recipient_name': recipient_name,
                'recipient_location': recipient_location,
                'recipient_postcode': recipient_postcode,
                'recipient_id': recipient_id
            }


def main():
    driver = PhantomJS()
    scraper = NLScraper(driver, year=2014)
    print(sys.argv[1])
    writer = unicodecsv.DictWriter(open(sys.argv[1], 'w'), ('amount', 'scheme', 'year',
        'country', 'currency', 'recipient_name', 'recipient_postcode',
        'recipient_id', 'recipient_location'))
    writer.writeheader()
    try:
        scraper.start(writer)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
