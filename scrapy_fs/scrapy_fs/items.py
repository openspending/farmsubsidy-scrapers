""" Item and Loader classes. """

# Farm subsidy data format:
# http://farmsubsidy.readthedocs.org/en/latest/scraper.html#scraper-data-format

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join

from scrapy_fs.scrubbers import (filter_euro_amount,
                                filter_croatian_recipient_id,
                                select_after_semicolon,
                                filter_croatian_postcode,
                                strip_line_breaks,
                                make_comma_proof,
                                filter_lithuanian_recipient_id,
                                filter_lithuanian_location)


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
    amount_in = MapCompose(filter_euro_amount, float)
    scheme_in = MapCompose(strip_line_breaks)
    recipient_id_in = MapCompose(filter_croatian_recipient_id)
    recipient_name_in = MapCompose(select_after_semicolon, make_comma_proof)
    recipient_location_in = MapCompose(select_after_semicolon)
    recipient_postcode_in = MapCompose(filter_croatian_postcode)


class LithuanianLoader(ItemLoader):
    default_output_processor = TakeFirst()

    year_in = MapCompose(int)
    amount_in = MapCompose(filter_euro_amount, float)
    recipient_id_in = MapCompose(filter_lithuanian_recipient_id, str)

    recipient_location_in = MapCompose(filter_lithuanian_location)
    recipient_location_out = Join(separator=', ')
