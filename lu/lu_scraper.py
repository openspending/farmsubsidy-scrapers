import scrapa


class LUScraper(scrapa.Scraper):
    BASE_URL = 'http://saturn.etat.lu/mafea/result.do'

    SCHEMES = ("I.1", "II.10", "III.3", "III.4", "III.7", "V/B.1.1", "V/B.1.2", "V/B.1.6", "V/B.1.8",
        "V/B.2.1", "V/B.2.4", "V/B.3.1", "V/B.3.2", "V/B.3.3", "V/B.3.4", "V/B.3.5", "V/B.3.6",
        "V/B.4.1", "V/B.4.2", "V/B.4.3", "V/B.4.4", "V/B.4.5",
    )

    YEARS = [2014, 2015]

    COMMUNES = ('(B) ARLON', '(B) Burg-Reuland', '(B) BASTOGNE', '(B) NAMUR', '(D) BITBURG-PRÜM',
        '(D) MERZIG-WADERN', '(D) Palzem', '(D) Schleiden', '(D) Trier-Land', '(D) TRIER-SAARBURG',
        '(F) DÉPARTEMENT MOSELLE', '(F) Redange', '(F) THIONVILLE-OUEST', 'Beaufort', 'Bech',
        'Beckerich', 'Berdorf', 'Bertrange', 'Bettembourg', 'Bettendorf', 'Betzdorf', 'Bissen',
        'Biwer', 'Boevange-sur-Attert', 'Boulaide', 'Bourscheid', 'Bous', 'Clervaux', 'Colmar-Berg',
        'Consdorf', 'Contern', 'CAPELLEN', 'CLERVAUX', 'Dalheim', 'Diekirch', 'Differdange',
        'Dippach', 'Dudelange', 'DIEKIRCH', 'Echternach', 'Ell', 'Erpeldange',
        'Erpeldange-sur-Sûre', 'Esch-sur-Alzette', 'Esch-sur-Sûre', 'Eschweiler',
        'Ettelbruck', 'ECHTERNACH', 'ESCH-SUR-ALZETTE', 'Feulen', 'Fischbach',
        'Flaxweiler', 'Frisange', 'Garnich', 'Goesdorf', 'Grevenmacher', 'Grosbous',
        'GREVENMACHER', 'Heffingen', 'Hesperange', 'Hobscheid', 'Junglinster', 'Käerjeng',
        'Kayl', 'Kehlen', 'Kiischpelt', 'Koerich', 'Kopstal', 'Lac de la Haute-Sûre',
        'Larochette', 'Lenningen', 'Leudelange', 'Lintgen', 'Lorentzweiler', 'Luxembourg',
        'LUXEMBOURG', 'Mamer', 'Manternach', 'Mersch', 'Mertert', 'Mertzig', 'Mompach',
        'Mondercange', 'Mondorf-les-Bains', 'MERSCH', 'Niederanven', 'Nommern', 'Pétange',
        'Parc Hosingen', 'Préizerdaul', 'Putscheid', 'Rambrouch', 'Reckange-sur-Mess',
        'Redange', 'Reisdorf', 'Remich', 'Roeser', 'Rosport', 'REDANGE', 'REMICH',
        'Saeul', 'Sandweiler', 'Sanem', 'Schengen', 'Schieren', 'Schuttrange',
        'Septfontaines', 'Stadtbredimus', 'Steinfort', 'Steinsel', 'Strassen',
        'Tandel', 'Troisvierges', 'Tuntange', 'Useldange', "Vallée de l'Ernz",
        'Vianden', 'Vichten', 'VIANDEN', 'Wahl', 'Waldbillig', 'Waldbredimus',
        'Walferdange', 'Weiler-la-Tour', 'Weiswampach', 'Wiltz', 'Wincrange',
        'Winseler', 'Wormeldange', 'WILTZ',)

    AMOUNTS = ('-1000000 ~ 0', '0~5000', '5000~10000', '10000~15000', '15000~20000', '20000~25000', '25000~30000', '30000~35000', '35000~40000', '40000~45000', '45000~50000', '50000~55000', '55000~60000', '60000~65000', '65000~70000', '70000~75000', '75000~80000', '80000~85000', '85000~90000', '90000~95000', '95000~100000', '100000~105000', '105000~110000', '110000~115000', '115000~120000', '120000~125000', '125000~130000', '130000~135000', '135000~140000', '140000~145000', '145000~150000', '150000~155000', '155000~160000', '160000~165000', '165000~170000', '170000~175000', '175000~180000', '180000~185000', '185000~190000', '190000~195000', '195000~200000', '200000~205000', '205000~210000', '210000~215000', '215000~220000', '220000~225000', '225000~230000', '230000~235000', '235000~240000', '240000~245000', '245000~250000', '250000~255000', '255000~260000', '260000~265000', '265000~270000', '270000~275000', '275000~280000', '280000~285000', '285000~290000', '290000~295000', '295000~300000', '300000~305000', '305000~310000', '310000~315000', '315000~320000', '320000~325000', '325000~330000', '330000~335000', '335000~340000', '340000~345000', '345000~350000', '350000 ~ 10000000',)

    ENCODING = 'ISO-8859-1'

    async def start(self):
        await self.schedule_many(self.download_year, self.get_queries())

    def get_queries(self):
        for year in self.YEARS:
            for c in self.COMMUNES:
                yield (year, c,), {}

    @scrapa.store
    async def download_year(self, year, commune):
        print('Running with', year, commune)
        with self.get_session() as session:
            await session.get()

            for amount_range in self.AMOUNTS:
                response = await session.post(data={
                    'year': str(year),
                    'fond': '',
                    'commune': commune,
                    'name': '',
                    'value': amount_range,
                    'action': 'Rechercher'
                })
                if 'Votre recherche ne retourne aucun résultat' in response.text(encoding=self.ENCODING):
                    continue
                try:
                    await self.extract_recipients(year, commune, amount_range, response.dom(encoding=self.ENCODING))
                except Exception as e:
                    print('Exception at', year, commune, amount_range)
                    raise e
        print('Done with', year, commune)

    async def extract_recipients(self, year, commune, amount_range, dom):
        datasets = []
        for div in dom.xpath('.//div[@class="fieldsetWrapper"]'):
            results = div.xpath('.//table[@class="results"]//tr[@class="results"]')
            name_row = results[0]
            name_tds = name_row.xpath('./td/text()')
            if len(name_tds) == 3:
                name = '%s %s' % (name_tds[1], name_tds[0])
                location = name_tds[2]
                recipient_id = None
            else:
                name = None
                recipient_id = name_tds[0]
                location = name_tds[1]

            if recipient_id is None:
                recipient_id = 'LU-%s-%s' % (location, name)
            else:
                recipient_id = 'LU-%s-%s' % (year, recipient_id)

            value_rows = results[1:-1]
            for value_row in value_rows:
                val = value_row.xpath('./td/text()')
                scheme = val[1]
                amount = float(val[2].replace('€', ''))
                year = int(val[0])
                data = {
                    'recipient_id': recipient_id,
                    'recipient_name': name,
                    'recipient_postcode': None,
                    'recipient_location': location,
                    'scheme': scheme,
                    'amount': amount,
                    'currency': 'EUR',
                    'country': 'LU',
                    'year': year,
                }
                datasets.append(data)

        key = '{year}${commune}$${amount}'.format(year=year, commune=commune,
              amount=amount_range)
        await self.store_result(key, 'result', datasets)


def main():
    scraper = LUScraper()
    scraper.run_from_cli()


if __name__ == '__main__':
    main()
