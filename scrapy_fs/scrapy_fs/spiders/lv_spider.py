import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


class LVSpider(Spider):
    name = "LV"

    START_URL = "https://eps.lad.gov.lv/payment_recipients?utf8=%E2%9C%93&eps_payment%5Bdisplay_name%5D=&eps_payment%5Btax_payer_number%5D=&eps_payment%5Bdistrict%5D=&eps_payment%5Bfund%5D=elf&eps_payment%5Bschema%5D=&eps_payment%5Bsum_from%5D=&eps_payment%5Bsum_to%5D=&eps_payment%5Byear_type%5D=F&eps_payment%5Byear%5D={year}&commit=Mekl%C4%93t&page={page}"

    def __init__(self, year=None):
        self.year = int(year)

    def start_requests(self):
        url = self.START_URL.format(year=self.year, page=1)
        yield scrapy.Request(url)

    def parse(self, response):
        page_count = response.xpath('//div[@id="paginate"]/a/text()')[-2].get()
        page_count = int(page_count)
        yield from self.parse_page(response)

        for i in range(2, page_count + 1):
            url = self.START_URL.format(year=self.year, page=i)
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        rows = response.xpath('//div[@id="pmt_rec_list"]/table/tr')
        value_rows = iter(rows[1:])
        for row in value_rows:
            # also read next row
            detail_row = next(value_rows)
            values = row.xpath("./td/text()")
            name = values[0].get().strip()
            location = values[1].get().strip()
            if name.isdigit():
                recipient_id = "{}-{}".format(
                    self.name, name
                )
                name = ""
            else:
                recipient_id = "{}-{}-{}".format(
                    self.name, slugify(name), slugify(location)
                )
            scheme_rows = detail_row.xpath(".//tr")[1:]
            for scheme_row in scheme_rows:
                cols = scheme_row.xpath("./td")
                scheme = cols[0].css("::text").get().strip()
                amount = float(cols[1].css("::text").get())
                yield FarmSubsidyItem(
                    year=self.year,
                    scheme=scheme.strip(),
                    amount=amount,
                    recipient_id=recipient_id,
                    recipient_name=name,
                    recipient_location=location,
                    country=self.name, currency='EUR',
                )
