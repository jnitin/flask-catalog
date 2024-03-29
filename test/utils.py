"""Utility functions to support unit testing with the flask test client"""

import pprint
import json

PPR = pprint.PrettyPrinter(indent=2)

def pprint_response(response, print_data=True):
    """Pretty print the response received by the flask test client"""

    print('\n--------------------------------------------------------------')
    print('RESPONSE STATUS CODE:')
    print(response)

    print('\nRESPONSE HEADER:')
    if response.headers is not None:
        PPR.pprint(response.headers.to_wsgi_list())
    else:
        print('response.headers has no content')

    print('\nRESPONSE DATA:')
    if print_data and response.data is not None:
        PPR.pprint(json.loads(response.data.decode()))
    else:
        print('response.data has no content')

    print('--------------------------------------------------------------')


def ordered(obj):
    """Sorts a json dictionary, so we can do a compare.

    Recursively sort any lists it finds,
    and convert dictionaries to lists of (key, value) pairs,
    so that they're orderable.

    IMPORTANT: It returns a sorted list, not a json dict !

    Taken from:
    https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa  # pylint: disable=line-to-long
    """
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())

    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)

    return obj
