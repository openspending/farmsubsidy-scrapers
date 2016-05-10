import re

import scrapy
from scrapy.spiders import Spider

from ..items import FarmSubsidyItem


class EESpider(Spider):
    name = "EE"
    YEAR = 2014

    AMOUNT_RE = re.compile('[^\d\.]')
    BAD_NAME = u'ID not available'

    SEARCH_PAGE = 'http://www.pria.ee/et/toetused/toetusesaajad/%d'

    start_urls = [
        'http://www.pria.ee/et/toetused/toetusesaajad/'
    ]

    def parse(self, response):
        # Do search post here
        # HTML Form doesn't work as action url is wrongly relative, do post manually
        # return scrapy.FormRequest.from_response(response, formxpath='//form[@id="receiversform"]', callback=self.search)

        return scrapy.Request(response.url, method='POST', callback=self.search, body='''csv=false&measure%5B%5D=ammlehmakasvatamiseta-iendavotsetoetus&measure%5B%5D=ebasoodsamatepiirkondadetoetusmak2004-2006&measure%5B%5D=edendusmeetmed-puu-jako-o-givilivib1&measure%5B%5D=ekf11riigiabikalapu-u-gialalisekslo_petamiseks&measure%5B%5D=ekf13kalalaevadepardaltehtavadinvesteeringudjaselektiivsus&measure%5B%5D=ekf14va-ikesemahulinerannapu-u-k&measure%5B%5D=ekf15sotsiaal-majanduslikudmeetmed&measure%5B%5D=ekf21vesiviljeluseinvesteeringutoetus&measure%5B%5D=ekf22sisevetekalandusetoetus&measure%5B%5D=ekf23investeeringudto-o-tlemissejaturustamisse&measure%5B%5D=ekf31u-histegevused&measure%5B%5D=ekf32veeloomastikuja-taimestikukaitsejaarendamine&measure%5B%5D=ekf33kalasadamadlossimiskohadjavarjualused&measure%5B%5D=ekf34uuteturgudearendaminejareklaamikampaaniad&measure%5B%5D=ekf35katseprojektid&measure%5B%5D=ekf41kalanduspiirkondadearendamine&measure%5B%5D=elatustaludekohanemisetoetusvb115&measure%5B%5D=heinaseemneta-iendavotsetoetus&measure%5B%5D=kalanduseturukorraldus&measure%5B%5D=kalandustoodetetootjakoolitustoetus&measure%5B%5D=kalandustoodetetootjapraktikatoetus&measure%5B%5D=keskkonnaso_bralikutootmisetoetusmak2004-2006&measure%5B%5D=koolipiimiii4&measure%5B%5D=koolipuuviliiii3&measure%5B%5D=meede11koolitus-jateavitustegevusedvb11&measure%5B%5D=meede12noortepo_llumajandustootjatetegevusealustaminevb12&measure%5B%5D=meede131-no_uandeteenustevo_imaldaminevb14&measure%5B%5D=meede132-no_uandesu-steemiarendaminevb15&measure%5B%5D=meede133no_uetelevastavusejato-o-ohutusealaseno_uandeteenusevo_imaldaminevb15&measure%5B%5D=meede141investeeringudmikropo_llumajandusettevo_tetearendamiseksvb16&measure%5B%5D=meede142investeeringudloomakasvatusehitistessevb16&measure%5B%5D=meede143investeeringudbioenergiatootmisessevb16&measure%5B%5D=meede15metsademajanduslikuva-a-rtuseparandaminejametsasaadustelelisandva-a-rtuseandminevb17&measure%5B%5D=meede161po_llumajandustoodetelejamittepuidulistemetsasaadusteto-o-tleminevb18&measure%5B%5D=meede162po_llumajandussektorijamahepo_llumajanudstootmisekohandumineuuteva-ljakutsetegavb18&measure%5B%5D=meede163-po_llumajandustoodeteu-histurustamiseedendaminevb18&measure%5B%5D=meede171po_llumaj-toidu-jametsandussektorikoosto-o-vb19&measure%5B%5D=meede18po_llu-jametsamajanduseinfrastruktuurvb110&measure%5B%5D=meede19tootjaru-hmadeloominejaarendaminevb116&measure%5B%5D=meede21ebasoodsamatepiirkondadetoetusvb22&measure%5B%5D=meede22naturapo_ldvb23&measure%5B%5D=meede231keskkonnaso_bralikmajandaminevb24&measure%5B%5D=meede232mahepo_llumajanduslikutootmisetoetusvb24&measure%5B%5D=meede233ohustatudto_uguloomakasvataminevb24&measure%5B%5D=meede234kohalikkusortitaimedvb24&measure%5B%5D=meede235poollooduslikukooslusehooldamisetoetusvb24&measure%5B%5D=meede24loomadekarjataminevb25&measure%5B%5D=meede251kiviaiarajamisejataastamisetoetusvb26&measure%5B%5D=meede27-natura2000alalasuvaerametsamaakohtaantavtoetusvb210&measure%5B%5D=meede31majandustegevusemitmekesistaminemaapiirkonnasvb31&measure%5B%5D=meede322ku-ladeuuendaminejaarendaminevb35&measure%5B%5D=meede4leadervb41vb43vb44vb45&measure%5B%5D=meede5tehnilineabivb5&measure%5B%5D=mesinduseeritoetusiii7&measure%5B%5D=piimalehmakasvatamiseta-iendavotsetoetus&measure%5B%5D=piimasektorieritoetusi7&measure%5B%5D=praktikatoetus&measure%5B%5D=puu-jako-o-giviljatagatis&measure%5B%5D=po_llukultuuridekasvatamiseta-iendavotsetoetus&measure%5B%5D=po_llumajanduskindlustustoetus&measure%5B%5D=po_llumajanduskultuurita-iendavotsetoetus&measure%5B%5D=po_llumajanduslikkeskkonnatoetuskiviaiadmak2004-2006&measure%5B%5D=po_llumajandusloomadearetustoetus&measure%5B%5D=po_llumajandustootjateasendamisetoetus&measure%5B%5D=riisitagatis&measure%5B%5D=teraviljatagatis&measure%5B%5D=toiduabiprogramm&measure%5B%5D=toiduabiprogrammidka-ibemaks&measure%5B%5D=turuarendustoetus&measure%5B%5D=utekasvatamiseta-iendavotsetoetus&measure%5B%5D=uteta-iendavotsetoetus&measure%5B%5D=veisekasvatamiseta-iendavotsetoetus&measure%5B%5D=u-htsepindalatoetusepo_himaksei2&type=payed&name=&county=&township=&indeks=&support_start=&support_end=&mak_04_06_start=&mak_04_06_end=&eafg_start=&eafg_end=&nat_support_start=&nat_support_end=&eur_fishf_start=&eur_fishf_end=&fish_marketf_start=&fish_marketf_end=&eafrd_start=&eafrd_end=&sum_start=&sum_end=&year=2014&currency=currency_eur&sorting=name_asc''')

    def search(self, response):
        max_page = int(response.css('a.page::text')[-1].extract())
        for i in range(1, max_page + 1):
            yield scrapy.Request(self.SEARCH_PAGE % i, self.search_page)

    def search_page(self, response):
        for href in response.css('table.info_tbl td:first-child a::attr(href)'):
            url = response.urljoin(href.extract())
            if not url.endswith('/eur'):
                url += '/eur'
            yield scrapy.Request(url, callback=self.parse_detail)

    def parse_detail(self, response):
        # http://www.pria.ee/et/toetused/toetusesaaja/u-lotammannivo_o_rikutalu/eur
        recipient_id = response.url.split('/')[-2]
        recipient_url = response.url
        recipient_name = response.xpath('.//div[@class="textpage"]/p/label[text()="Saaja nimi:"]/following-sibling::text()')[0].extract()
        recipient_name = recipient_name.strip()
        if recipient_name == recipient_id:
            recipient_name = ''

        recipient_id = 'EE-' + recipient_id

        county = response.xpath('.//div[@class="textpage"]/p/label[text()="Maakond:"]/following-sibling::text()')
        if county:
            county = county[0].extract().strip()
        else:
            county = ''

        parish = response.xpath('.//div[@class="textpage"]/p/label[text()="Vald:"]/following-sibling::text()')
        if parish:
            parish = parish[0].extract().strip()
        else:
            parish = ''
        recipient_location = ', '.join(c for c in [county, parish] if c)

        for tr in response.xpath('.//table[@id="supportstable"]/tbody/tr'):
            year = int(tr.xpath('./td[1]/text()').extract_first())
            scheme = tr.xpath('./td[3]/a/text()').extract_first()

            amount = tr.xpath('./td[11]/text()').extract_first()
            try:
                amount = float(self.AMOUNT_RE.sub('', amount.replace(',', '.')))
            except ValueError:
                continue

            yield FarmSubsidyItem(
                year=year,
                scheme=scheme,
                amount=amount,
                recipient_id=recipient_id,
                recipient_name=recipient_name,
                recipient_location=recipient_location,
                recipient_url=recipient_url,
                country='EE', currency='EUR',
            )
