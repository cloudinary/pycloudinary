import json
import socket

import certifi
import cloudinary.account
import urllib3
from urllib3.exceptions import HTTPError

import cloudinary
from cloudinary.api import EXCEPTION_CODES, GeneralError

logger = cloudinary.logger

_http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)

PROVISIONING = "provisioning"
ACCOUNT = "accounts"


class Response(dict):
    def __init__(self, result, response, **kwargs):
        super(Response, self).__init__(**kwargs)
        self.update(result)


def call_api(method, uri, params, **options):
    return _call_api(method, uri, params=params, **options)


def _call_api(method, uri, params=None, body=None, headers=None, **options):
    prefix = options.pop("upload_prefix",
                         cloudinary.config().upload_prefix) or "https://api.cloudinary.com"
    account_id = options.pop("account_id", cloudinary.account.account_config().account_id)
    if not account_id:
        raise Exception("Must supply account_id")
    api_key = options.pop("api_key", cloudinary.account.account_config().provisioning_api_key)
    if not api_key:
        raise Exception("Must supply api_key")
    api_secret = options.pop("api_secret", cloudinary.account.account_config().provisioning_api_secret)
    if not api_secret:
        raise Exception("Must supply api_secret")
    api_url = "/".join(
        [prefix, "v1_1", PROVISIONING, ACCOUNT, cloudinary.account.account_config().account_id] + uri)

    processed_params = None
    if isinstance(params, dict):
        processed_params = {}
        for key, value in params.items():
            if isinstance(value, list) or isinstance(value, tuple):
                value_list = {"{}[{}]".format(key, i): i_value for i, i_value in enumerate(value)}
                processed_params.update(value_list)
            elif value != None:
                processed_params[key] = value

    # Add authentication
    req_headers = urllib3.make_headers(
        basic_auth="{0}:{1}".format(api_key, api_secret),
        user_agent=cloudinary.get_user_agent()
    )
    if headers is not None:
        req_headers.update(headers)
    kw = {}
    if 'timeout' in options:
        kw['timeout'] = options['timeout']
    if body is not None:
        kw['body'] = body
    try:
        response = _http.request(method.upper(), api_url, processed_params, req_headers, **kw)
        body = response.data
    except HTTPError as e:
        raise GeneralError("Unexpected error {0}", e.message)
    except socket.error as e:
        raise GeneralError("Socket Error: %s" % (str(e)))

    try:
        result = json.loads(body.decode('utf-8'))
    except Exception as e:
        # Error is parsing json
        raise GeneralError("Error parsing server response (%d) - %s. Got - %s" % (response.status, body, e))

    if "error" in result:
        exception_class = EXCEPTION_CODES.get(response.status) or Exception
        exception_class = exception_class
        raise exception_class("Error {0} - {1}".format(response.status, result["error"]["message"]))

    return Response(result, response)
