""" A bunch of pipelines. """

from scrapy.exceptions import DropItem


class CroatianNationalSubsidyFilter(object):
    """ Filters out subsidy items corresponding to national schemes. """

    @staticmethod
    def process_item(item, spider):
        args = (spider.name, item['scheme'], item['recipient_name'])
        if 'nacionalna' in item['agency'].lower():
            raise DropItem('%s dropped national subsidy item "%s" for %s' % args)
        else:
            return item
