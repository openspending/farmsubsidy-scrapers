# Farmsubsidy data format, see:
# http://farmsubsidy.readthedocs.org/en/latest/scraper.html#scraper-data-format
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ScrapyFsItem(Item):
    rName = Field()
    rAdress1 = Field()
    rAdress2 = Field()
    rZipcode = Field()
    rTown = Field()
    globalSchemeID = Field()
    amountEuro = Field()
