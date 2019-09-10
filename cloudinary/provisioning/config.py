from __future__ import absolute_import

from copy import deepcopy
import os
import logging
import re
import numbers
from math import ceil
from six import python_2_unicode_compatible, string_types
from cloudinary import import_django_settings
from cloudinary.http_client import HttpClient
from cloudinary.compat import urlparse, parse_qs

class ProvisioningConfig(object):
    def __init__(self):
        django_settings = import_django_settings()
        if django_settings:
            self.update(**django_settings)
        elif os.environ.get("CLOUDINARY_ACCOUNT_ID"):
            self.update(
                account_id=os.environ.get("CLOUDINARY_ACCOUNT_ID"),
                api_key=os.environ.get("CLOUDINARY_PROVISIONING_API_KEY"),
                api_secret=os.environ.get("CLOUDINARY_PROVISIONING_API_SECRET"),
            )
        elif os.environ.get("CLOUDINARY_ACCOUNT_URL"):
            cloudinary_url = os.environ.get("CLOUDINARY_ACCOUNT_URL")
            self._parse_cloudinary_account_provisioning_url(cloudinary_url)

    def _parse_cloudinary_account_provisioning_url(self, cloudinary_url):
        uri = urlparse(cloudinary_url.replace("cloudinary://", "http://"))
        for k, v in parse_qs(uri.query).items():
            if self._is_nested_key(k):
                self._put_nested_key(k, v)
            else:
                self.__dict__[k] = v[0]
        self.update(
            account_id=uri.hostname,
            api_key=uri.username,
            api_secret=uri.password,
        )
        if uri.path != '':
            self.update(secure_distribution=uri.path[1:])

    def __getattr__(self, i):
        if i in self.__dict__:
            return self.__dict__[i]
        else:
            return None

    def update(self, **keywords):
        for k, v in keywords.items():
            self.__dict__[k] = v

    def _is_nested_key(self, key):
        return re.match(r'\w+\[\w+\]', key)

    def _put_nested_key(self, key, value):
        chain = re.split(r'[\[\]]+', key)
        chain = [k for k in chain if k]
        outer = self.__dict__
        last_key = chain.pop()
        for inner_key in chain:
            if inner_key in outer:
                inner = outer[inner_key]
            else:
                inner = dict()
                outer[inner_key] = inner
            outer = inner
        if isinstance(value, list):
            value = value[0]
        outer[last_key] = value

def config(**keywords):
    global _provisioning_config
    _provisioning_config.update(**keywords)
    return _provisioning_config


def reset_config():
    global _provisioning_config
    _provisioning_config = ProvisioningConfig()


_provisioning_config = ProvisioningConfig()
_http_client = HttpClient()
