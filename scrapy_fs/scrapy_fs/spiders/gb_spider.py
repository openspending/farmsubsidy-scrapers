import re
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy_fs.items import ScrapyFsItem
from scrapy.contrib.loader import ItemLoader

class GbSpider(Spider):
    '''
    WORK IN PROGRESS... (2014-03-13)
    Author   : Holger Drewes (@HolgerD77)
    Creation : 2014-03-13 
    Updated  : -
    Command  : "scrapy crawl GB -a year=YEAR"
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
    
    def parse(self, response):
        return [FormRequest.from_response(response,
                formdata={ 
                    'ctl00$Center$ContentPlaceHolder1$SearchControls1$ddlFinancialYear' : self.year,
                },
                formnumber=1,
                callback=self.after_form_submit)]
    
    def after_form_submit(self, response):
        filename = response.url.split("/")[-2]
        open(filename, 'wb').write(response.body)
        
        sel = Selector(response)
        entries = sel.xpath('//table[@class="resultstable"]/tr')
        
        #Schemes being used
        #"GB1";;"Direct payments under European Agricultural Guarantee Fund";;"GB"
        #"GB2";;"Other payments under European Agricultural Guarantee Fund";;"GB"
        #"GB3";;"European Agricultural Fund for Rural Development";;"GB"
        schemes = [
            (u'GB1', '4'),
            #(u'GB2', '5'),
            #(u'GB3', '6'),
        ]
        
        items = []
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
                            items.append(l.load_item())
                    except ValueError:
                        continue
        
        return items
    