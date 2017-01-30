import hashlib
import time
from binascii import a2b_hex
import hmac
import six

from cloudinary import AKAMAI_TOKEN_NAME
import cloudinary


def digest(message, key):
    bin_key = a2b_hex(key)
    return hmac.new(bin_key, message.encode('utf-8'), hashlib.sha256).hexdigest()


def generate(acl, start_time=None, window=None, end_time=None, ip=None, key=None,
             token_name=AKAMAI_TOKEN_NAME):
    if key is None:
        key = cloudinary.config().akamai_key
    expiration = end_time
    if expiration is None:
        if window is not None:
            start = start_time if start_time is not None else int(time.mktime(time.gmtime()))
            expiration = start + window
        else:
            raise Exception("Must provide either end_time or window")

    token_parts = []
    if ip is not None: token_parts.append("ip=" + ip)
    if start_time is not None: token_parts.append("st=%d" % start_time)
    token_parts.append("exp=%d" % expiration)
    token_parts.append("acl=%s" % acl)
    auth = digest("~".join(token_parts), key)
    token_parts.append("hmac=%s" % auth)
    return "%(token_name)s=%(token)s" % {"token_name": token_name, "token": "~".join(token_parts)}
