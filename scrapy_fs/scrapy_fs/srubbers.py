""" A bunch of scrubbers that can be chained into processors. """


from re import search


def filter_euro_amount(amount):
    return amount.replace(' HRK', '').replace('.', '').replace(',', '.')


def select_after_semicolon(location):
    return location.split(': ')[-1]


def filter_croatian_recipient_id(url):
    return url.split('/')[-1]


def filter_croatian_postcode(location):
    return search(r'\d+$', location).group(0)


def strip_line_breaks(text):
    return text.strip('\n').strip('\r')


def filter_lithuanian_recipient_id(raw_id):
    return raw_id[1:]


def filter_lithuanian_location(location):
    # Get rid of the words 'municipality' and 'region' and
    return location.replace(u'apskritis', '').replace(u'rajonas', '').strip()


def make_comma_proof(text):
    if ',' in text:
        return '"' + text + '"'
    else:
        return text
