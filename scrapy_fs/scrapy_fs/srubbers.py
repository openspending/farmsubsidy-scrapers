""" A bunch of scrubbers that can be chained into processors. """

from re import search


def filter_croatian_amount(amount):
    return float(amount.replace(' HRK', '').replace('.', '').replace(',', '.'))


def filter_croatian_location(location):
    return location.split(': ')[-1]


def filter_croatian_recipient_id(url):
    return url.split('/')[-1]


def filter_croatian_postcode(location):
    return search(r'\d+$', location).group(0)
