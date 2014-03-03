# Copyright Cloudinary
import sys

PY3 = (sys.version_info.major == 3)

if PY3:
    import http.client as httplib
    NotConnected = httplib.NotConnected
    import urllib.request as urllib2
    from io import StringIO
    from urllib.parse import urlencode, unquote, urlparse, parse_qs
    to_bytes = lambda s: s.encode('utf8')
    to_string = lambda b: b.decode('utf8')
    string_types = (str)
else:
    import httplib
    from httplib import NotConnected
    import StringIO
    import urllib2
    from urllib import urlencode, unquote
    from urlparse import urlparse, parse_qs
    to_bytes = str
    to_string = str
    string_types = (str, unicode)
