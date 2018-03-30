"""Utility functions to support end-2-end testing with python-requests module,
as used by our jupyter notebook."""

import pprint
import json

from tests_utils import pprint_sequence, ordered

def pprint_request(request, print_body=True):
    """Pretty print a request send by python-requests module"""
    # See:
    # http://docs.python-requests.org/en/master/user/quickstart/#make-a-request
    # http://docs.python-requests.org/en/master/user/advanced/#request-and-response-objects

    print('\n--------------------------------------------------------------')
    print('REQUEST METHOD and URL:')
    print ('{} {}'.format(request.method, request.url))

    print('\nREQUEST HEADER:')
    if request.headers is not None:
        # convert CaseInsensitiveDict into dict before pretty printing
        # https://stackoverflow.com/questions/4301069/any-way-to-properly-pretty-print-ordered-dictionaries
        pprint_sequence(dict(request.headers))
    else:
        print ('request.headers is empty')

    if print_body:
        print('\nREQUEST BODY:')
        if request.body is not None:
            pprint_sequence(json.loads(request.body.decode()))
        else:
            print ('request.body is empty')

    # you can break here in the debugger to further explore the body
    ...

    print('--------------------------------------------------------------')


def pprint_response(r, print_text=True, print_content=False):
    """Pretty print the response received by python-requests module"""
    # See:
    # http://docs.python-requests.org/en/master/user/quickstart/#make-a-request
    # http://docs.python-requests.org/en/master/user/advanced/#request-and-response-objects

    print('\n--------------------------------------------------------------')
    print('RESPONSE STATUS CODE:')
    print (r.status_code)

    print('\nRESPONSE HEADER:')
    if r.headers is not None:
        # convert CaseInsensitiveDict into dict before pretty printing
        # https://stackoverflow.com/questions/4301069/any-way-to-properly-pretty-print-ordered-dictionaries
        pprint_sequence(dict(r.headers))
    else:
        print ('r.headers is empty')

    if print_text:
        print('\nRESPONSE TEXT (Body):')
        if r.text is not None:
            pprint_sequence(json.loads(r.text))
        else:
            print ('r.text is empty')

    if print_content:
        print('\nRESPONSE CONTENT (Body):')
        if r.content is not None:
            pprint_sequence(json.loads(r.content.decode()))
        else:
            print ('r.content is empty')

    print('--------------------------------------------------------------')
