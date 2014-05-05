# Checks for Farmsubsidy data format
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem


class FormatValidationPipeline(object):
    
    def process_item(self, item, spider):
        
        if 'rName' not in item or not item['rName']:
            raise DropItem("Missing name in %s" % item)
        
        if 'globalSchemeID' not in item or not item['globalSchemeID']:
            raise DropItem("Missing globalSchemeID in %s" % item)
        
        if ('amountEuro' not in item or item['amountEuro'] == None) and \
           ('amountNationalCurrency' not in item or item['amountNationalCurrency'] == None):
            raise DropItem("Item %s missing both amountEuro and amountNationalCurrency" % item)
        
        return item
