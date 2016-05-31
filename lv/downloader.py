# coding: utf-8
""" This is a selenium downloader for the Latvian website. """


# The form for requesting data is https://eps.lad.gov.lv/payment_recipients.
# The form gives you the option of downloading a csv file... which is cool.
# Requesting all the data at once times out however. So the way to go is to
# request subsidy schemes one by one and pray to the god of APIs.

from csv import QUOTE_ALL
from logging import getLogger, basicConfig, DEBUG
from os.path import join, exists
from pandas import read_csv, set_option
from requests import get
from slugify import slugify


set_option('display.expand_frame_repr', False)
basicConfig(level=DEBUG, format='[%(module)s] %(message)s')
log = getLogger(__name__)
line = 300 * '-'


class DataFragment(object):
    BASE_URL = 'https://eps.lad.gov.lv/payment_recipients?'
    BUCKET = '/home/loic/output/farm-subsidies'
    CHUNK_SIZE = 512 * 1024

    def __init__(self, scheme, year=2014):
        self.year = int(year)
        self.scheme = scheme
        self.query = {
            'commit': u'Meklēt',
            'eps_payment[fund]': 'elf',
            'eps_payment[schema]': 'L111.14',
            'eps_payment[year]': self.year,
            'eps_payment[year_type]': 'K',
            'format': 'csv',
            'utf8': u'✓'
        }
        self.description = 'scheme %s, year %s' % (self.scheme, self.year)

    @property
    def url(self):
        parameters = [key + '=' + 'value' for key, value in self.query.items()]
        return self.BASE_URL + '&'.join(parameters)

    def download(self):
        self.query.update({'eps_payment[schema]': self.scheme})
        response = get(self.BASE_URL, params=self.query)
        self._save_to_cache(response)
        log.debug('Saved %s', self.filepath)

    def _save_to_cache(self, response):
        chunks = response.iter_content(chunk_size=self.CHUNK_SIZE)
        with open(self.filepath, 'w+') as cache:
            for chunk in chunks:
                if chunk:
                    cache.write(chunk)

    @property
    def filepath(self):
        parts = ['latvia', str(self.year), self.scheme]
        filename = slugify(unicode('_'.join(parts)))
        return join(self.BUCKET, filename + '.csv')

    @property
    def df_raw(self):
        columns = ['recipient_name', 'recipient_location', 'scheme', 'amount']

        # I ask for utf-8 and get utf-16 back... wtf?
        dataframe = read_csv(self.filepath,
                             sep=';',
                             quoting=QUOTE_ALL,
                             skiprows=[0, 1, 2],
                             encoding='utf-16',
                             names=columns)

        log.info('Loaded %s (%s rows)', self.description, dataframe.shape[0])
        return dataframe

    @property
    def is_cached(self):
        if exists(self.filepath):
            log.debug('Found %s in cache', self.filepath)
            return True
        else:
            return False


class Aggregator(object):
    SCHEMES = [
        'L111.14',
        'L002'
        # 'L141'
        # 'L112'
        # 'NATURA',
        # 'ZRG',
        # 'L006;L005',
        # 'L312.21;L312.02;L312.03;L312.11;L312.01',
        # 'ACM',
        # 'ARKIR',
        # 'BDUZ',
        # 'BLA',
        # 'VEI',
        # 'PAAP',
        # 'FDA',
        # 'A004',
        # 'INTVK',
        # 'L125',
        # 'IDIV',
        # 'INZPIE;INZPUA;TKODSRP',
        # 'IKC',
        # 'ISA',
        # 'ILA',
        # 'IPKV',
        # 'NIM',
        # 'L411',
        # 'L123',
        # 'L223',
        # 'L4132.03;L4132.02;L4131.05;L4132.04;L4132.01;L4131.01;L4132.05;L4131.02;L4131.03'
    ]

    def __init__(self, year=2014):
        self.year = year

    @property
    def fragments(self):
        for scheme in self.SCHEMES:
            fragment = DataFragment(scheme)
            if not fragment.is_cached:
                fragment.download()
            yield fragment

    def transform(self):
        for fragment in self.fragments:
            df = fragment.df_raw.ffill()
            df = df[df['scheme'] != str(fragment.year)]
            df['year'] = 2014
            df['recipient_url'] = fragment.url
            df['recipient_postcode'] = None
            df['recipient_country'] = 'LV'
            df['recipient_address'] = None
            df['currency'] = 'EUR'
            df['recipient_id'] = map(slugify, df['recipient_name'])
            log.debug('Fragment %s has %s rows: \n%s\n%s\n%s',
                      fragment.description,
                      df.shape[0],
                      line,
                      df.head(),
                      line)

if __name__ == '__main__':
    aggregator = Aggregator(2014)
    aggregator.transform()
