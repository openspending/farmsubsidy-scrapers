import re

import scrapy
from scrapy.spiders import Spider

from ..items import FarmSubsidyItem


class CZSpider(Spider):
    name = "CZ"
    YEAR = 2015

    AMOUNT_RE = re.compile('[^\d\.]')
    BAD_NAME = u'ID not available'

    PAGE_URL = 'http://www.szif.cz/irj/portal/eng/list_of_beneficiaries?asc=asc&page={page}&sortby=%2FBIC%2FZC_F201&ino=0&year=' + str(YEAR)

    start_urls = [
        'http://www.szif.cz/irj/portal/eng/list_of_beneficiaries?name=&nuts4=&obec=&opatr=&cod=&cdo=&filter=search&page=1&asc=asc&sortby=%2FBIC%2FZC_F201&year=' + str(YEAR)
    ]

    def parse(self, response):
        page_count = response.xpath('.//div[@class = "pagination"][1]//ul//li[a/@class = "show-loading"][last()]/a/text()')[0].extract()
        page_count = int(page_count)
        for i in range(1, page_count + 1):
            yield scrapy.Request(self.PAGE_URL.format(page=i), callback=self.parse_page)

    def parse_page(self, response):
        for href in response.xpath('.//div[@class="container-table"]/table//tr/td[1]//a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_detail)

    def parse_detail(self, response):
        # http://www.szif.cz/irj/portal/eng/list_of_beneficiaries?ji=1001057805&opatr=&year=&portalAction=detail
        recipient_url = response.url
        url_part = response.url.split('ji=', 1)[1]
        recipient_id = 'CZ-' + url_part.split('&')[0]

        recipient_name = response.xpath('.//div[@class="section"]/h3/text()')[0].extract()
        if recipient_name == self.BAD_NAME:
            recipient_name = ''

        recipient_location = response.xpath('.//div[@class="section"]/h3/following-sibling::div/text()')
        if recipient_location:
            recipient_location = recipient_location[0].extract()
        else:
            recipient_location = ''

        for tr in response.xpath('.//div[@class="section"]//table//tr'):
            content_list = [c.extract() for c in tr.xpath('./td/text()')]
            if not content_list:
                continue
            scheme = content_list[2].split('-', 1)[0]

            # Use EU Sources for amounts (5th column)
            amount = content_list[4].replace(',', '.')
            amount = float(self.AMOUNT_RE.sub('', amount))

            yield FarmSubsidyItem(
                year=content_list[0],
                scheme=scheme,
                amount=amount,
                recipient_id=recipient_id,
                recipient_name=recipient_name,
                recipient_location=recipient_location,
                recipient_url=recipient_url,
                country='CZ', currency='CZK',
            )
