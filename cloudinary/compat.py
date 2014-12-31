# Copyright Cloudinary
import sys

PY3 = (sys.version_info[0] == 3)

if PY3:
    import http.client as httplib
    NotConnected = httplib.NotConnected
    import urllib.request as urllib2
    import urllib.error
    HTTPError = urllib.error.HTTPError
    from io import StringIO, BytesIO
    from urllib.parse import urlencode, unquote, urlparse, parse_qs, quote_plus
    to_bytes = lambda s: s.encode('utf8')
    to_bytearray = lambda s: bytearray(s, 'utf8')
    to_string = lambda b: b.decode('utf8')
    string_types = (str)
else:
    import httplib
    from httplib import NotConnected
    from io import BytesIO
    import StringIO
    import urllib2
    HTTPError = urllib2.HTTPError
    from urllib import urlencode, unquote, quote_plus
    from urlparse import urlparse, parse_qs
    to_bytes = str
    to_bytearray = str
    to_string = str
    string_types = (str, unicode)

try:
    advance_iterator = next
except NameError:
    def advance_iterator(it):
        return it.next()
