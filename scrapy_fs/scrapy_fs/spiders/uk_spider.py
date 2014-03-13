from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy_fs.items import ScrapyFsItem
from scrapy.contrib.loader import ItemLoader

class UkSpider(Spider):
    '''
    WORK IN PROGRESS... (2014-03-13)
    Author   : Holger Drewes (@HolgerD77)
    Creation : 2014-03-13 
    Updated  : -
    Command  : "scrapy crawl UK -a year=YEAR"
    '''
    
    name = "UK"
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
        
        items = []
        for entry in entries:
            l = ItemLoader(ScrapyFsItem(), entry)
            l.add_xpath('rName', 'td[1]/text()')
            
            items.append(l.load_item())
        
        return items
    