import re
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest, Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy_fs.items import ScrapyFsItem
from scrapy.contrib.loader import ItemLoader

class GbSpider(Spider):
    '''
    Author   : Holger Drewes (@HolgerD77)
    Creation : 2014-03-13 
    Updated  : -
    Command  : "scrapy crawl GB -a year=YEAR [-a num_pages=PAGES_TO_CRAWL] [-o payment_YEAR.txt -t csv]"
    '''
    
    name = "GB"
    allowed_domains = ["defra.gov.uk"]
    start_urls = [
        "http://cap-payments.defra.gov.uk/",
    ]
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('year'):
            self.year = kwargs.get('year')
        else:
            raise CloseSpider("Please provide a year in the form: -a year=YEAR")
        if kwargs.get('num_pages'):
            self.num_pages = int(kwargs.get('num_pages'))    
    
    def parse(self, response):
        request = FormRequest.from_response(response,
                formdata={ 
                    'ctl00$Center$ContentPlaceHolder1$SearchControls1$ddlFinancialYear' : self.year,
                },
                formnumber=1,
                callback=self.after_form_submit)
        request.meta['page'] = 1
        return [request]
    
    def after_form_submit(self, response):
        page = response.request.meta['page']
        print "Crawling page %d..." % page
        sel = Selector(response)
        entries = sel.xpath('//table[@class="resultstable"]/tr')
        
        #Schemes being used
        #"GB1";;"Direct payments under European Agricultural Guarantee Fund";;"GB"
        #"GB2";;"Other payments under European Agricultural Guarantee Fund";;"GB"
        #"GB3";;"European Agricultural Fund for Rural Development";;"GB"
        schemes = [
            (u'GB1', '5'),
            (u'GB3', '4'),
        ]
        
        for entry in entries:
            for scheme in schemes:
                l = ItemLoader(ScrapyFsItem(), entry)
                l.add_xpath('rName', 'td[1]/text()')
                l.add_xpath('rZipcode', 'td[2]/text()')
                l.add_xpath('rTown', 'td[3]/text()')
                l.add_value('globalSchemeID', scheme[0])
                
                amount = entry.xpath('td[' + scheme[1] + ']/text()').extract()
                if len(amount) > 0:
                    try:
                        amount_str = re.sub('[\xa3,\s]+', '', amount[0])
                        amount_float = float(amount_str)
                        if amount_float > 0:
                            l.add_value('amountNationalCurrency', amount_float)
                            yield l.load_item()
                    except ValueError:
                        continue
        
        new_page = page + 1
        load_next = True
        if hasattr(self, 'num_pages') and self.num_pages < new_page:
            load_next = False
        
        if len(entries) > 0 and load_next:
            url = 'http://cap-payments.defra.gov.uk/SearchResults.aspx?Page=%d&Sort=' % new_page
            request = Request(url, callback=self.after_form_submit)
            request.meta['page'] = new_page
        
            yield request
    