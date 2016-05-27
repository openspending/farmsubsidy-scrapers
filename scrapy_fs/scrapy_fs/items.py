# Farmsubsidy data format, see:
# http://farmsubsidy.readthedocs.org/en/latest/scraper.html#scraper-data-format
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose

from scrapy_fs.srubbers import filter_croatian_amount, filter_croatian_recipient_id, select_after_semicolon, \
    filter_croatian_postcode


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


class CroatiaItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    year_in = MapCompose(int)
    amount_in = MapCompose(filter_croatian_amount)
    recipient_id_in = MapCompose(filter_croatian_recipient_id)
    recipient_name_in = MapCompose(select_after_semicolon)
    recipient_location_in = MapCompose(select_after_semicolon)
    recipient_postcode_in = MapCompose(filter_croatian_postcode)
