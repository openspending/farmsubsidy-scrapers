import re

import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


class MTSpider(Spider):
    name = "MT"
    YEAR = 2014
    NUM_ONLY_RE = re.compile('^[\s\d]+$')

    start_urls = [
        'https://environment.gov.mt/en/ARPA/Pages/Payments.aspx'
    ]

    def parse(self, response):
        return scrapy.FormRequest.from_response(response, callback=self.search)

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
            data = dict(zip(keys, tds))
            recipient_name = data.pop('Name')
            recipient_location = data.pop('Locality')
            recipient_postcode = data.pop('Postcode')
            data.pop('Grand_Total')
            if self.NUM_ONLY_RE.match(recipient_name):
                recipient_id = 'MT-%s-%s' % (self.YEAR, recipient_name)
                recipient_name = ''
            else:
                recipient_id = 'MT-%s-%s' % (recipient_postcode, slugify(recipient_name))

            for scheme, amount in data.items():
                if not amount:
                    continue
                amount = float(amount)
                yield FarmSubsidyItem(
                    year=self.YEAR,
                    scheme=scheme,
                    amount=amount,
                    recipient_id=recipient_id,
                    recipient_name=recipient_name,
                    recipient_location=recipient_location,
                    recipient_postcode=recipient_postcode,
                    country='MT', currency='EUR',
                )
