# Farmsubsidy data format, see:
# http://farmsubsidy.readthedocs.org/en/latest/scraper.html#scraper-data-format
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst

class ScrapyFsItem(Item):
    rName = Field(
        output_processor=TakeFirst(),
    )
    rAdress1 = Field(
        output_processor=TakeFirst(),
    )
    rAdress2 = Field(
        output_processor=TakeFirst(),
    )
    rZipcode = Field(
        output_processor=TakeFirst(),
    )
    rTown = Field(
        output_processor=TakeFirst(),
    )
    globalSchemeID = Field(
        output_processor=TakeFirst(),
    )
    amountEuro = Field(
        output_processor=TakeFirst(),
    )
    amountNationalCurrency = Field(
        output_processor=TakeFirst(),
    )
