from __future__ import absolute_import

import os

from cloudinary import BaseConfig, import_django_settings

ACCOUNT_URI_SCHEME = "account"


class AccountConfig(BaseConfig):
    def __init__(self):
        self._uri_scheme = ACCOUNT_URI_SCHEME
        django_settings = import_django_settings()
        if django_settings:
            self.update(**django_settings)
        elif os.environ.get("CLOUDINARY_ACCOUNT_URL"):
            account_url = os.environ.get("CLOUDINARY_ACCOUNT_URL")
            parsed_url = self._parse_cloudinary_url(account_url)
            self._setup_from_parsed_url(parsed_url)

    def _config_from_parsed_url(self, parsed_url):
        if not self._is_url_scheme_valid(parsed_url):
            raise ValueError("Invalid CLOUDINARY_ACCOUNT_URL scheme. URL should begin with 'account://'")

        return {
            "account_id": parsed_url.hostname,
            "provisioning_api_key": parsed_url.username,
            "provisioning_api_secret": parsed_url.password,
        }


def account_config(**keywords):
    global _account_config
    _account_config.update(**keywords)
    return _account_config


def reset_config():
    global _account_config
    _account_config = AccountConfig()


_account_config = AccountConfig()
