import json
import re
import sys

import dataset
import unicodecsv
from slugify import slugify


NUMONLY_RE = re.compile('^\d+$')


def main():
    writer = unicodecsv.DictWriter(sys.stdout,
            ('recipient_id', 'recipient_name',
             'recipient_location', 'amount', 'scheme',
             'currency', 'country', 'year'))
    writer.writeheader()
    db = dataset.connect('sqlite:///ie_data.db')
    for row in db['scrapa_result']:
        row = json.loads(row['result'])
        year = int(row['year'])
        recipient_location = '%s, %s' % (row['municipal'].strip(), row['location'])
        if NUMONLY_RE.match(row['name']):
            recipient_id = 'IE-%d-%s' % (year, row['name'])
            recipient_name = ''
        else:
            recipient_id = 'IE-%d-%s-%s' % (year, slugify(recipient_location),
                            slugify(row['name']))
            recipient_name = row['name']

        for scheme_amount in row['amounts']:
            writer.writerow({
                'recipient_id': recipient_id,
                'recipient_name': recipient_name,
                'recipient_location': recipient_location,
                'amount': scheme_amount[1],
                'scheme': scheme_amount[0],
                'year': year,
                'currency': 'EUR',
                'country': 'IE'
            })


if __name__ == '__main__':
    main()
