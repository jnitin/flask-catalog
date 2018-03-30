"""Utility functions to support unit testing with the flask test client"""

import pprint
import json

def pprint_sequence(sequence):
    if (sequence is not None and len(sequence)>0):
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(sequence)
    else:
        print ('sequence has no content')


def pprint_response(response, print_data=True):
    """Pretty print the response received by the flask test client"""

    print('\n--------------------------------------------------------------')
    print('RESPONSE STATUS CODE:')
    print (response)

    print('\nRESPONSE HEADER:')
    if response.headers is not None:
        pprint_sequence(response.headers.to_wsgi_list())
    else:
        print ('response.headers has no content')


    print('\nRESPONSE DATA:')
    if print_data and response.data is not None:
        pprint_sequence(json.loads(response.data.decode()))
    else:
        print ('response.data has no content')

    print('--------------------------------------------------------------')

def ordered(obj):
    """Sorts a json dictionary, so we can do a compare.

    Recursively sort any lists it finds,
    and convert dictionaries to lists of (key, value) pairs,
    so that they're orderable.

    IMPORTANT: It returns a sorted list, not a json dict !

    Taken from:
    https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa  # NOQA
    """
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
