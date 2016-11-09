# Copyright Cloudinary
import six.moves.urllib.parse
urlencode = six.moves.urllib.parse.urlencode
unquote = six.moves.urllib.parse.unquote
urlparse = six.moves.urllib.parse.urlparse
parse_qs = six.moves.urllib.parse.parse_qs
quote_plus = six.moves.urllib.parse.quote_plus
import six.moves.http_client as httplib
from io import StringIO, BytesIO
from six import PY3, string_types


if PY3:
    to_bytes = lambda s: s.encode('utf8')
    to_bytearray = lambda s: bytearray(s, 'utf8')
    to_string = lambda b: b.decode('utf8')

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
