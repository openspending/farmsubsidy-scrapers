# coding: utf-8
""" Download and aggregate CSV files from the Latvian website.

Usage:
    lt_downloader.py [--year=YEAR] [--bucket=BUCKET]

Options:
    --year=YEAR       Calendar year [default: 2014]
    --bucket=BUCKET   File dump directory [default: ~/output/farm-subsidies/]

"""


# The form for requesting data is https://eps.lad.gov.lv/payment_recipients.
# The form gives you the option of downloading a csv file... which is cool.
# Requesting all the data at once times out however. So the way to go is to
# request subsidy schemes one by one and stitch them together.


from csv import QUOTE_ALL
from logging import getLogger, basicConfig, DEBUG
from os.path import join, exists, expanduser
from docopt import docopt
from pandas import read_csv, set_option, DataFrame, concat
from requests import get
from slugify import slugify


SCHEMES = [
    'L111.14',
    'L002'
    'L141'
    'L112'
    'NATURA',
    'ZRG',
    'L006;L005',
    'L312.21;L312.02;L312.03;L312.11;L312.01',
    'ACM',
    'ARKIR',
    'BDUZ',
    'BLA',
    'VEI',
    'PAAP',
    'FDA',
    'A004',
    'INTVK',
    'L125',
    'IDIV',
    'INZPIE;INZPUA;TKODSRP',
    'IKC',
    'ISA',
    'ILA',
    'IPKV',
    'NIM',
    'L411',
    'L123',
    'L223',
    'L4132.03;L4132.02;L4131.05;L4132.04;L4132.01;L4131.01;L4132.05;L4131.02;L4131.03'
]


set_option('display.expand_frame_repr', False)
basicConfig(level=DEBUG, format='[%(module)s] %(message)s')
log = getLogger(__name__)


class Fragment(object):
    BASE_URL = 'https://eps.lad.gov.lv/payment_recipients?'

    def __init__(self, scheme, year, bucket):
        self.year = int(year)
        self.scheme = scheme
        self.description = '%s %s' % (year, scheme)
        self.bucket = bucket

        self.response = None
        self.data = None

        self.query = {
            'commit': u'Meklēt',
            'eps_payment[fund]': 'elf',
            'eps_payment[schema]': 'L111.14',
            'eps_payment[year]': self.year,
            'eps_payment[year_type]': 'K',
            'format': 'csv',
            'utf8': u'✓'
        }

        log.info('Fetching data for %s', self.description)

    def download(self):
        self.query.update({'eps_payment[schema]': self.scheme})
        self.response = get(self.BASE_URL, params=self.query)
        self._save_to_cache()

        log.debug('Saved %s', self.filepath)

    def _save_to_cache(self):
        chunks = self.response.iter_content(chunk_size=512*1024)
        with open(self.filepath, 'w+') as cache:
            for chunk in chunks:
                if chunk:
                    cache.write(chunk)

    def load_from_csv(self):
        columns = ['recipient_name',
                   'recipient_location',
                   'scheme',
                   'amount']

        # I ask the API for utf-8 and get utf-16 back... wtf?
        self.data = read_csv(self.filepath,
                             sep=';',
                             quoting=QUOTE_ALL,
                             skiprows=[0, 1, 2],
                             encoding='utf-16',
                             names=columns)

        log.info('Loaded %s', self.description)
        self.log_dataframe()

    def cleanup(self):
        self.data.ffill(inplace=True)
        self.data.where(self.data_rows_only, inplace=True)

        self.data['recipient_id'] = self.recipient_ids
        self.data['recipient_url'] = self.url
        self.data['recipient_country'] = 'LV'
        self.data['currency'] = 'EUR'
        self.data['year'] = self.year

        self.data['recipient_postcode'] = None
        self.data['recipient_address'] = None

        log.info('Cleaned up %s', self.description)
        self.log_dataframe()

    def log_dataframe(self):
        log.debug('Dataframe has %s rows: \n%s\n%s\n%s',
                  len(self.data), 300 * '-', self.data.head(10), 300 * '-')

    @property
    def filepath(self):
        parts = ['latvia', str(self.year), self.scheme]
        filename = slugify(unicode('_'.join(parts)))
        return join(self.bucket, 'latvia', filename + '.csv')

    @property
    def is_cached(self):
        if exists(self.filepath):
            log.debug('Found %s in cache', self.filepath)
            return True
        else:
            return False

    @property
    def recipient_ids(self):
        return map(slugify, map(unicode, self.data['recipient_name']))

    @property
    def data_rows_only(self):
        return self.data['scheme'] != str(self.year)

    @property
    def url(self):
        parameters = [key + '=' + 'value' for key, value in self.query.items()]
        return self.BASE_URL + '&'.join(parameters)


def bulk_download(year, bucket):
    bucket = expanduser(bucket)
    filepath = bucket + 'latvia' + str(year) + '.csv'
    data = DataFrame()

    for scheme in SCHEMES:
        fragment = Fragment(scheme, year, bucket)

        if not fragment.is_cached:
            fragment.download()

        fragment.load_from_csv()
        fragment.cleanup()

        data = concat([data, fragment.data], ignore_index=True)
        log.debug('Added %s rows to bulk dataframe', len(fragment.data))

    data.to_csv(filepath, encoding='utf-8', mode='w+')
    data.drop_duplicates(inplace=True)
    log.info('Bulk download saved to %s', filepath)


if __name__ == '__main__':
    options = docopt(__doc__)
    bulk_download(options['--year'], options['--bucket'])
