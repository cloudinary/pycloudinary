from __future__ import absolute_import

import os

from cloudinary.__init__ import import_django_settings
from cloudinary.compat import urlparse, parse_qs
from cloudinary.http_client import HttpClient


class AccountConfig(object):
    def __init__(self):
        django_settings = import_django_settings()
        if django_settings:
            self.update(**django_settings)
        elif os.environ.get("CLOUDINARY_ACCOUNT_URL"):
            account_url = os.environ.get("CLOUDINARY_ACCOUNT_URL")
            self._parse_cloudinary_account_url(account_url)

    def _parse_cloudinary_account_url(self, account_url):
        uri = urlparse(account_url.replace("account://", "http://"))
        for k, v in parse_qs(uri.query).items():
            if self._is_nested_key(k):
                self._put_nested_key(k, v)
            else:
                self.__dict__[k] = v[0]
        self.update(
            account_id=uri.hostname,
            provisioning_api_key=uri.username,
            provisioning_api_secret=uri.password,
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


def account_config(**keywords):
    global _account_config
    _account_config.update(**keywords)
    return _account_config


def reset_config():
    global _account_config
    _account_config = AccountConfig()


_account_config = AccountConfig()
_http_client = HttpClient()
