import json

import scrapy
from scrapy.spiders import Spider

from ..items import FarmSubsidyItem


class EESpider(Spider):
    name = "EE"
    BASE_URL = "https://www.pria.ee"
    START_URL = "https://www.pria.ee/toetused/toetusesaajad?type=payed&year={year}&name=&county=&township=&indeks=&mp%5B352%5D=352&mp%5B350%5D=350&mp%5B348%5D=348&mp%5B342%5D=342&mp%5B340%5D=340&mp%5B607%5D=607&mp%5B606%5D=606&mp%5B320%5D=320&mp%5B597%5D=597&mp%5B331%5D=331&mp%5B333%5D=333&mp%5B336%5D=336&mp%5B328%5D=328&mp%5B379%5D=379&mp%5B329%5D=329&mp%5B330%5D=330&mp%5B343%5D=343&mp%5B321%5D=321&mp%5B332%5D=332&mp%5B1253%5D=1253&mp%5B335%5D=335&mp%5B353%5D=353&mp%5B355%5D=355&mp%5B1254%5D=1254&mp%5B334%5D=334&mp%5B354%5D=354&mp%5B375%5D=375&mp%5B338%5D=338&mp%5B1724%5D=1724&mp%5B370%5D=370&mp%5B367%5D=367&mp%5B322%5D=322&mp%5B351%5D=351&mp%5B341%5D=341&mp%5B349%5D=349&mp%5B357%5D=357&mp%5B344%5D=344&mp%5B327%5D=327&mp%5B339%5D=339&mp%5B376%5D=376&mp%5B345%5D=345&mp%5B356%5D=356&mp%5B230%5D=230&mp%5B1723%5D=1723&mp%5B390%5D=390&mp%5B1255%5D=1255&mp%5B1727%5D=1727&mp%5B1256%5D=1256&mp%5B256%5D=256&mp%5B311%5D=311&mp%5B306%5D=306&mp%5B285%5D=285&mp%5B603%5D=603&mp%5B1257%5D=1257&mp%5B309%5D=309&mp%5B307%5D=307&mp%5B1258%5D=1258&mp%5B1725%5D=1725&mp%5B315%5D=315&mp%5B1726%5D=1726&mp%5B599%5D=599&mp%5B310%5D=310&mp%5B366%5D=366&mp%5B263%5D=263&mp%5B246%5D=246&mp%5B293%5D=293&mp%5B365%5D=365&mp%5B364%5D=364&mp%5B1259%5D=1259&mp%5B373%5D=373&mp%5B595%5D=595&mp%5B266%5D=266&mp%5B267%5D=267&mp%5B1260%5D=1260&mp%5B299%5D=299&mp%5B359%5D=359&mp%5B282%5D=282&mp%5B1261%5D=1261&mp%5B600%5D=600&mp%5B270%5D=270&mp%5B284%5D=284&mp%5B308%5D=308&mp%5B323%5D=323&mp%5B347%5D=347&mp%5B358%5D=358&mp%5B289%5D=289&mp%5B598%5D=598&mp%5B593%5D=593&mp%5B337%5D=337&mp%5B601%5D=601&mp%5B605%5D=605&mp%5B231%5D=231&mp%5B276%5D=276&mp%5B227%5D=227&mp%5B298%5D=298&mp%5B362%5D=362&mp%5B290%5D=290&mp%5B260%5D=260&mp%5B592%5D=592&mp%5B240%5D=240&mp%5B243%5D=243&mp%5B324%5D=324&mp%5B346%5D=346&mp%5B233%5D=233&ma%5B1504%5D=1504&ma%5B1505%5D=1505&ma%5B1508%5D=1508&ma%5B1626%5D=1626&ma%5B1510%5D=1510&ma%5B1511%5D=1511&ma%5B1561%5D=1561&ma%5B1693%5D=1693&ma%5B1631%5D=1631&ma%5B1707%5D=1707&ma%5B1571%5D=1571&ma%5B1695%5D=1695&ma%5B1557%5D=1557&ma%5B1684%5D=1684&ma%5B1559%5D=1559&ma%5B1701%5D=1701&ma%5B1608%5D=1608&ma%5B1708%5D=1708&ma%5B1580%5D=1580&ma%5B1687%5D=1687&ma%5B1581%5D=1581&ma%5B1689%5D=1689&ma%5B1583%5D=1583&ma%5B1688%5D=1688&ma%5B1585%5D=1585&ma%5B1690%5D=1690&ma%5B1587%5D=1587&ma%5B1691%5D=1691&ma%5B1629%5D=1629&ma%5B1692%5D=1692&ma%5B1593%5D=1593&ma%5B1686%5D=1686&ma%5B1567%5D=1567&ma%5B1685%5D=1685&ma%5B1573%5D=1573&ma%5B1705%5D=1705&ma%5B1575%5D=1575&ma%5B1712%5D=1712&ma%5B1563%5D=1563&ma%5B1703%5D=1703&ma%5B1660%5D=1660&ma%5B1636%5D=1636&ma%5B1667%5D=1667&ma%5B1639%5D=1639&ma%5B1628%5D=1628&ma%5B1661%5D=1661&ma%5B1640%5D=1640&ma%5B1730%5D=1730&ma%5B1720%5D=1720&ma%5B1493%5D=1493&ma%5B1494%5D=1494&ma%5B1721%5D=1721&ma%5B1495%5D=1495&ma%5B1642%5D=1642&ma%5B1664%5D=1664&ma%5B1740%5D=1740&ma%5B1632%5D=1632&ma%5B1633%5D=1633&ma%5B1719%5D=1719&ma%5B1496%5D=1496&ma%5B1715%5D=1715&ma%5B1733%5D=1733&ma%5B1498%5D=1498&ma%5B1659%5D=1659&ma%5B1732%5D=1732&ma%5B1668%5D=1668&ma%5B1681%5D=1681&ma%5B1500%5D=1500&ma%5B1519%5D=1519&ma%5B1702%5D=1702&ma%5B1502%5D=1502&ma%5B1704%5D=1704&ma%5B1509%5D=1509&ma%5B1663%5D=1663&ma%5B1514%5D=1514&ma%5B1515%5D=1515&ma%5B1722%5D=1722&ma%5B1517%5D=1517&ma%5B1741%5D=1741&ma%5B1569%5D=1569&ma%5B1706%5D=1706&ma%5B1540%5D=1540&ma%5B1666%5D=1666&ma%5B1716%5D=1716&ma%5B1736%5D=1736&ma%5B1717%5D=1717&ma%5B1737%5D=1737&ma%5B1656%5D=1656&ma%5B1651%5D=1651&ma%5B1652%5D=1652&ma%5B1653%5D=1653&ma%5B1654%5D=1654&ma%5B1655%5D=1655&ma%5B1657%5D=1657&ma%5B1658%5D=1658&ma%5B1521%5D=1521&ma%5B1522%5D=1522&ma%5B1671%5D=1671&ma%5B1523%5D=1523&ma%5B1524%5D=1524&ma%5B1644%5D=1644&ma%5B1634%5D=1634&ma%5B1641%5D=1641&ma%5B1545%5D=1545&ma%5B1546%5D=1546&ma%5B1710%5D=1710&ma%5B1526%5D=1526&ma%5B1734%5D=1734&ma%5B1645%5D=1645&ma%5B1547%5D=1547&ma%5B1550%5D=1550&ma%5B1650%5D=1650&ma%5B1729%5D=1729&ma%5B1527%5D=1527&ma%5B1699%5D=1699&ma%5B1713%5D=1713&ma%5B1665%5D=1665&ma%5B1728%5D=1728&ma%5B1553%5D=1553&ma%5B1554%5D=1554&ma%5B1680%5D=1680&ma%5B1731%5D=1731&ma%5B1555%5D=1555&ma%5B1627%5D=1627&ma%5B1533%5D=1533&ma%5B1534%5D=1534&ma%5B1535%5D=1535&ma%5B1683%5D=1683&ma%5B1538%5D=1538&ma%5B1700%5D=1700&ma%5B1738%5D=1738&ma%5B1739%5D=1739&ma%5B1742%5D=1742&ma%5B1743%5D=1743&ma%5B1606%5D=1606&ma%5B1638%5D=1638&ma%5B1649%5D=1649&ma%5B1682%5D=1682&ma%5B1604%5D=1604&ma%5B1675%5D=1675&ma%5B1610%5D=1610&ma%5B1662%5D=1662&ma%5B1735%5D=1735&ma%5B1647%5D=1647&ma%5B1670%5D=1670&ma%5B1577%5D=1577&ma%5B1672%5D=1672&ma%5B1589%5D=1589&ma%5B1598%5D=1598&ma%5B1674%5D=1674&ma%5B1625%5D=1625&ma%5B1677%5D=1677&ma%5B1595%5D=1595&ma%5B1596%5D=1596&ma%5B1711%5D=1711&ma%5B1600%5D=1600&ma%5B1714%5D=1714&ma%5B1542%5D=1542&ma%5B1543%5D=1543&ma%5B1544%5D=1544&ma%5B1709%5D=1709&ma%5B1591%5D=1591&ma%5B1678%5D=1678&ma%5B1669%5D=1669&ma%5B1612%5D=1612&ma%5B1613%5D=1613&ma%5B1718%5D=1718&ma%5B1622%5D=1622&ma%5B1673%5D=1673&ma%5B1676%5D=1676&ma%5B1616%5D=1616&ma%5B1565%5D=1565&ma%5B1620%5D=1620&ma%5B1679%5D=1679&ma%5B1618%5D=1618&eafrd%5Bfrom%5D=&eafrd%5Bto%5D=&nat_support%5Bfrom%5D=&nat_support%5Bto%5D=&emkf%5Bfrom%5D=&emkf%5Bto%5D=&eagf%5Bfrom%5D=&eagf%5Bto%5D=&eagf_other%5Bfrom%5D=&eagf_other%5Bto%5D=&support%5Bfrom%5D=&support%5Bto%5D=&sum%5Bfrom%5D=&sum%5Bto%5D=&page={page}"

    def __init__(self, year=None):
        # self.year = int(year)
        self.year = "all"

    def start_requests(self):
        # Use high page number to get max page count
        url = self.START_URL.format(year=self.year, page=10000)
        yield scrapy.Request(url)

    def parse(self, response):
        page_count = int(response.css('.page-item.active .page-link::text').get())
        print("Page count: {}".format(page_count))
        # page starts at 0
        for i in range(page_count + 1):
            url = self.START_URL.format(year=self.year, page=i)
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        row_hrefs = response.css('table a.use-ajax::attr(href)').getall()
        for href in row_hrefs:
            url = "{}{}".format(self.BASE_URL, href)
            yield scrapy.Request(url, callback=self.parse_detail)

    def parse_detail(self, response):
        body = response.text
        json_body = body[len("<textarea>"):-len("</textarea>")].strip()
        weird_drupal_data = json.loads(json_body)
        html = [x for x in weird_drupal_data if x["command"] == "openBootstrap4Dialog"][0]["data"]
        root = scrapy.Selector(text=html)
        recipient_name, county, muni, recipient_index = root.css(".modal-body .row .col-6 p strong::text").getall()
        recipient_name = recipient_name.strip()
        county = county.strip()
        muni = muni.strip()
        recipient_index = recipient_index.strip()
        if recipient_name.isdigit():
            recipient_id = "{}-{}".format(
                self.name, recipient_name
            )
            recipient_name = ""
        else:
            recipient_id = "{}-index-{}".format(
                self.name, recipient_index
            )
        recipient_location = "{}, {}".format(muni, county)
        rows = root.css(".modal-body #recipient_table tbody tr")
        for row in rows:
            value_cols = row.css("td")
            values = [col.css("::text").get() for col in value_cols]

            year = int(values[0].strip())
            scheme = values[1].strip()
            money_values = [v.strip() for v in values[2:-1] if v]
            money_values = [float(v.replace(" ", "").replace(",", ".")) for v in money_values if v]
            if len(money_values) > 1:
                raise Exception("Multiple money values at %s", response.request.url)

            yield FarmSubsidyItem(
                year=year,
                scheme=scheme,
                amount=money_values[0],
                recipient_id=recipient_id,
                recipient_name=recipient_name,
                recipient_location=recipient_location,
                country=self.name, currency='EUR',
            )
