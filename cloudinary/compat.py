# Copyright Cloudinary
from six import PY3

import six.moves.urllib.parse

urlencode = six.moves.urllib.parse.urlencode
unquote = six.moves.urllib.parse.unquote
urlparse = six.moves.urllib.parse.urlparse
parse_qs = six.moves.urllib.parse.parse_qs
parse_qsl = six.moves.urllib.parse.parse_qsl
quote_plus = six.moves.urllib.parse.quote_plus
httplib = six.moves.http_client
urllib2 = six.moves.urllib.request
NotConnected = six.moves.http_client.NotConnected

if PY3:
    def to_bytes(s):
        return s.encode('utf8')

    def to_bytearray(s):
        bytearray(s, 'utf8')

    def to_string(b):
        b.decode('utf8')
else:
    to_bytes = str
    to_bytearray = str
    to_string = str

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
