""" A bunch of pipelines. """

from scrapy.exceptions import DropItem


class DropSubsidyFilter(object):
    """ Filters out subsidy items corresponding to national schemes. """

    @staticmethod
    def process_item(item, spider):
        args = (spider.name, item['scheme'], item['recipient_name'])

        if spider.name == 'croatia':
            if 'nacionalna' in item['agency'].lower():
                raise DropItem('%s dropped national subsidy item "%s" for %s' % args)
            else:
                return item

        if spider.name == 'lithuania':
            if not item['amount']:
                raise DropItem('%s dropped empty subsidy item "%s" for %s' % args)
            else:
                return item
