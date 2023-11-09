import scrapy
from scrapy.spiders import Spider

from slugify import slugify

from ..items import FarmSubsidyItem


class LUSpider(Spider):
    name = "LU"

    BASE_URL = "https://agriculture.public.lu"
    START_URL = "https://agriculture.public.lu/de/beihilfen/beguenstigte-der-agrarbeihilfen.html?annee={year}&mesure=&municipalite=&nom=&montantbas=&montanthaut=&numeroPage={page}"

    def __init__(self, year=None):
        self.year = int(year)

    def start_requests(self):
        url = self.START_URL.format(year=self.year, page=1)
        yield scrapy.Request(url)

    def parse(self, response):
        next_url = response.css(".pagination-next a.icon-right::attr(href)").get()
        if next_url:
            yield scrapy.Request(self.BASE_URL + next_url)

        yield from self.parse_page(response)

    def parse_page(self, response):
        rows = response.css('.accordion-gestion details')
        for row in rows:
            # also read next row
            name = row.css("summary .gestion-name::text").get().strip()
            location = row.css("summary .gestion-city::text").get().strip()
            if name.endswith('_Anonymisiert'):
                recipient_id = "{}-{}-{}".format(
                    self.name, self.year, name.split("_")[0]
                )
                name = ""
            else:
                recipient_id = "{}-{}-{}".format(
                    self.name, slugify(name), slugify(location)
                )

            scheme_rows = row.css("table tr")[1:]
            for scheme_row in scheme_rows:
                cols = scheme_row.xpath("./td")
                scheme = cols[0].css("b::text").get()
                if scheme is None:
                    scheme = "<empty>"
                amount = float(cols[1].xpath("./text()").get().replace('€', '').strip())
                yield FarmSubsidyItem(
                    year=self.year,
                    scheme=scheme.strip(),
                    amount=amount,
                    recipient_id=recipient_id,
                    recipient_name=name,
                    recipient_location=location,
                    country=self.name, currency='EUR',
                )
