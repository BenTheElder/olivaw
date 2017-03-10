from __future__ import print_function

import sys

# python 3
if sys.version_info >= (3, 0):
    # python 3 imports and exports
    from urllib import request
    from configparser import SafeConfigParser
    import queue

    def request_urlopen(req, *args, **kwargs):
        ctx = request.urlopen(req, *args, **kwargs)
        return ctx

    def to_bytes(string, enc):
        return bytes(string, enc)

# python 2
else:
    # python 2 imports and exports
    import urllib2 as request
    import contextlib
    from ConfigParser import SafeConfigParser
    import Queue as queue

    def request_urlopen(req, *args, **kwargs):
        ctx = contextlib.closing(request.urlopen(req, *args, **kwargs))
        return ctx

    def to_bytes(string, enc):
        return string.encode(enc)
