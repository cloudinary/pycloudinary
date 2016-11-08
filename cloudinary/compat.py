# Copyright Cloudinary
import sys
import urllib3

PY3 = (sys.version_info[0] == 3)

if PY3:
    import http.client as httplib
    import urllib.request as urllib2
    import urllib.error
    from io import StringIO, BytesIO
    from urllib.parse import urlencode, unquote, urlparse, parse_qs, quote_plus
    to_bytes = lambda s: s.encode('utf8')
    to_bytearray = lambda s: bytearray(s, 'utf8')
    to_string = lambda b: b.decode('utf8')
    string_types = (str)

else:
    import httplib
    from io import BytesIO
    import StringIO
    import urllib2
    from urllib import urlencode, unquote, quote_plus
    from urlparse import urlparse, parse_qs
    to_bytes = str
    to_bytearray = str
    to_string = str
    string_types = (str, unicode)

try:
    cldrange = xrange
except NameError:
    def cldrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

try:
    advance_iterator = next
except NameError:
    def advance_iterator(it):
        return it.next()
