import urllib3

import cloudinary
from cloudinary import API_VERSION
from cloudinary.api_client.execute_request import execute_request
from cloudinary.provisioning.account_config import account_config
from cloudinary.utils import process_params, get_http_connector


PROVISIONING_SUB_PATH = "provisioning"
ACCOUNT_SUB_PATH = "accounts"
_http = get_http_connector(account_config(), cloudinary.CERT_KWARGS)


def call_account_api(method, uri, params, **options):
    return _call_account_api(method, uri, params=params, **options)


def _call_account_api(method, uri, params=None, body=None, headers=None, **options):
    prefix = options.pop("upload_prefix",
                         cloudinary.config().upload_prefix) or "https://api.cloudinary.com"
    account_id = options.pop("account_id", account_config().account_id)
    if not account_id:
        raise Exception("Must supply account_id")
    provisioning_api_key = options.pop("api_key", account_config().provisioning_api_key)
    if not provisioning_api_key:
        raise Exception("Must supply provisioning_api_key")
    provisioning_api_secret = options.pop("api_secret",
                                          account_config().provisioning_api_secret)
    if not provisioning_api_secret:
        raise Exception("Must supply provisioning_api_secret")
    provisioning_api_url = "/".join(
        [prefix, API_VERSION, PROVISIONING_SUB_PATH, ACCOUNT_SUB_PATH, account_id] + uri)

    processed_params = process_params(params)

    # Add authentication
    req_headers = urllib3.make_headers(
        basic_auth="{0}:{1}".format(provisioning_api_key, provisioning_api_secret),
        user_agent=cloudinary.get_user_agent()
    )
    if headers is not None:
        req_headers.update(headers)
    kw = {}
    if 'timeout' in options:
        kw['timeout'] = options['timeout']
    if body is not None:
        kw['body'] = body

    return execute_request(http_connector=_http,
                           method=method,
                           params=processed_params,
                           req_headers=req_headers,
                           api_url=provisioning_api_url,
                           **kw)
