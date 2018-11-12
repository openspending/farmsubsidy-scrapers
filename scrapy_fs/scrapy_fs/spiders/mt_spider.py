import re

import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


YEAR = 2017


class MTSpider(Spider):
    name = "MT"

    NUM_ONLY_RE = re.compile('^[\s\d]+$')

    start_urls = [
        'https://msdec.gov.mt/en/arpa/Pages/Payments.aspx'
    ]

    def __init__(self, year=YEAR):
        self.year = int(year)

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'ctl00$ctl28$g_c7852a28_8677_47de_bf51_102e5afe2ae8$AELSg_c7852a28_8677_47de_bf51_102e5afe2ae8combo5': str(self.year),
                '__SCROLLPOSITIONX': '0',
                '__SCROLLPOSITIONY': '0',
                '__LASTFOCUS': '',
                'search': '0',
                '__EVENTARGUMENT': '',
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '1',
                '__EVENTTARGET': '',
                'InputKeywords': 'Search',
            },
            callback=self.search)

    def search(self, response):
        current_page = response.xpath('//tr[@class="AELSpager"]//table//td[span]')
        if current_page:
            print('Page %s' % current_page[0].extract())
        else:
            print('No current page!')
        trs = response.xpath('.//table[starts-with(@class, "AELStable")]//tr')
        keys = None
        for i, tr in enumerate(trs):
            if i == 0:
                keys = [x.extract().strip() for x in tr.xpath('./th//text()')]
                continue
            if tr.xpath('self::*[@class = "AELSpager"]'):
                '''
<a href="javascript:__doPostBack('ctl00$ctl24$g_cd62d2d8_1d36_4059_ab03_0a01e96a3be3$ctl08','Page$3')">3</a>
                function __doPostBack(eventTarget, eventArgument) {
    if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
        theForm.__EVENTTARGET.value = eventTarget;
        theForm.__EVENTARGUMENT.value = eventArgument;
        theForm.submit();
    }
}
                '''
                # Find next link
                next_link = response.xpath('//tr[@class="AELSpager"]//table//td[span]/following-sibling::td/a/@href')
                if not next_link:
                    continue
                next_link = next_link[0].extract()
                next_link = next_link.replace("javascript:__doPostBack('", '')
                next_link = next_link.split("','")
                event_target = next_link[0]
                event_arg = next_link[1].replace("')", '')

                yield scrapy.FormRequest.from_response(response,
                    callback=self.search,
                    dont_click=True,
                    formdata={
                        '__EVENTTARGET': event_target,
                        '__EVENTARGUMENT': event_arg
                    })
                return
            tds = [x.extract().strip() for x in tr.xpath('./td//text()')]
            if len(tds) != len(keys):
                return
            data = dict(zip(keys, tds))
            recipient_name = data.pop('Name')
            recipient_location = data.pop('Locality')
            recipient_postcode = data.pop('Postcode')
            year = data.pop('Financial Year', None)
            if year is None:
                return
            data.pop('Grand_Total')
            if self.NUM_ONLY_RE.match(recipient_name):
                recipient_id = 'MT-%s-%s' % (year, recipient_name)
                recipient_name = ''
            else:
                recipient_id = 'MT-%s-%s' % (recipient_postcode, slugify(recipient_name))

            for scheme, amount in data.items():
                if not amount:
                    continue
                amount = float(amount.replace(',', ''))
                if not amount:
                    continue
                yield FarmSubsidyItem(
                    year=int(year),
                    scheme=scheme,
                    amount=amount,
                    recipient_id=recipient_id,
                    recipient_name=recipient_name,
                    recipient_location=recipient_location,
                    recipient_postcode=recipient_postcode,
                    country='MT', currency='EUR',
                )
