import csv
import json
import sys

import dataset


def clean_location(location):
    location = location.strip().replace(', Stadt', '')
    return location


def main():
    db = dataset.connect('sqlite:///de_data.db')
    writer = csv.DictWriter(sys.stdout, ('recipient_name', 'recipient_id',
            'recipient_postcode', 'recipient_location', 'scheme', 'amount',
            'currency', 'year', 'country'),delimiter=';')
    writer.writeheader()
    for line in db['scrapa_result']:
        data = json.loads(line['result'])
        for scheme_name, scheme_amounts in data['schemes'].items():
            for amount in scheme_amounts:
                writer.writerow({
                    'recipient_name': data['name'] if data['name'] != 'Kleinempfänger' else '',
                    'recipient_id': '%s-%s' % ('DE', line['result_id']),
                    'recipient_postcode': 'DE-%s' % data['plz'],
                    'recipient_location': clean_location(data['location']),
                    'scheme': scheme_name,
                    'amount': str(amount),
                    'currency': 'EUR',
                    'year': data['jahr'],
                    'country': 'DE'
                })


if __name__ == '__main__':
    main()
