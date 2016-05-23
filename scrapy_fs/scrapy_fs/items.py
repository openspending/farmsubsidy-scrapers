# Farmsubsidy data format, see:
# http://farmsubsidy.readthedocs.org/en/latest/scraper.html#scraper-data-format
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class FarmSubsidyItem(Item):
    year = Field()
    country = Field()  # Two letters ISO 3166
    recipient_id = Field()
    recipient_name = Field()
    recipient_address = Field()
    recipient_postcode = Field()
    recipient_location = Field()
    recipient_url = Field()
    agency = Field()
    scheme = Field()
    amount = Field()
    currency = Field()
