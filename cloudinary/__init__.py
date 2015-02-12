from __future__ import absolute_import

import os
import sys

CF_SHARED_CDN = "d3jpl91pxevbkh.cloudfront.net"
OLD_AKAMAI_SHARED_CDN = "cloudinary-a.akamaihd.net"
AKAMAI_SHARED_CDN = "res.cloudinary.com"
SHARED_CDN = AKAMAI_SHARED_CDN
CL_BLANK = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

VERSION = "1.0.21"
USER_AGENT = "cld-python-" + VERSION

from cloudinary import utils
from cloudinary.compat import urlparse, parse_qs

def import_django_settings():
    try:
        import django.conf
        from django.core.exceptions import ImproperlyConfigured
        try:
            if 'CLOUDINARY' in dir(django.conf.settings):
                return django.conf.settings.CLOUDINARY
            else:
                return None
        except ImproperlyConfigured:
            return None
    except ImportError:
        return None

class Config(object):
    def __init__(self):
        django_settings = import_django_settings()
        if django_settings:
            self.update(**django_settings)
        elif os.environ.get("CLOUDINARY_CLOUD_NAME"):
            self.update(
              cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
              api_key = os.environ.get("CLOUDINARY_API_KEY"),
              api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
              secure_distribution = os.environ.get("CLOUDINARY_SECURE_DISTRIBUTION"),
              private_cdn = os.environ.get("CLOUDINARY_PRIVATE_CDN") == 'true'
            )
        elif os.environ.get("CLOUDINARY_URL"):
            uri = urlparse(os.environ.get("CLOUDINARY_URL").replace("cloudinary://", "http://"))
            for k, v in parse_qs(uri.query).items():
                self.__dict__[k] = v[0]
            self.update(
              cloud_name = uri.hostname,
              api_key = uri.username,
              api_secret = uri.password,
              private_cdn = uri.path != ''
            )
            if uri.path != '':
                self.update(secure_distribution = uri.path[1:])
    def __getattr__(self, i):
        if i in self.__dict__:
            return self.__dict__[i]
        else:
            return None

    def update(self, **keywords):
        for k, v in keywords.items():
            self.__dict__[k] = v

_config = Config()

def config(**keywords):
    global _config
    _config.update(**keywords)
    return _config

def reset_config():
    global _config
    _config = Config()

class CloudinaryImage(object):
    def __init__(self, public_id = None, format = None, version = None,
            signature = None, url_options = {}, metadata = None, type = None):

        self.metadata = metadata
        metadata = metadata or {}
        self.public_id = public_id or metadata.get('public_id')
        self.format = format or metadata.get('format')
        self.version = version or metadata.get('version')
        self.signature = signature or metadata.get('signature')
        self.type = type or metadata.get('type') or "upload"
        self.url_options = url_options

    def __unicode__(self):
        return self.public_id

    def validate(self):
        expected = utils.api_sign_request({"public_id": self.public_id, "version": self.version}, config().api_secret)
        return self.signature == expected

    @property
    def url(self):
        return self.build_url(**self.url_options)

    def __build_url(self, **options):
        combined_options = dict(format = self.format, version = self.version, type = self.type)
        combined_options.update(options)
        return utils.cloudinary_url(self.public_id, **combined_options)        
      
    def build_url(self, **options):
        return self.__build_url(**options)[0]

    def image(self, **options):
        src, attrs = self.__build_url(**options)
        responsive = attrs.pop("responsive", False)
        hidpi = attrs.pop("hidpi", False)
        if responsive or hidpi:
            attrs["data-src"] = src
            classes = "cld-responsive" if responsive else "cld-hidpi"
            if "class" in attrs: classes += " " + attrs["class"] 
            attrs["class"] = classes
            src = attrs.pop("responsive_placeholder", config().responsive_placeholder)
            if src == "blank": src = CL_BLANK 
        
        attrs = sorted(attrs.items())
        if src: attrs.insert(0, ("src", src))

        return u"<img {0}/>".format(' '.join([u"{0}='{1}'".format(key, value) for key, value in attrs if value]))
