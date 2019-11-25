import json
import socket

import urllib3
from urllib3.exceptions import HTTPError

import cloudinary
from cloudinary import utils
import cloudinary.provisioning.account
from cloudinary.exceptions import GeneralError, EXCEPTION_CODES

logger = cloudinary.logger

_http = utils.get_http_connector(cloudinary.config(), cloudinary.CERT_KWARGS)

PROVISIONING_SUB_PATH = "provisioning"
ACCOUNT_SUB_PATH = "accounts"


def _call_provisioning_api(method, uri, params=None, body=None, headers=None, **options):
    prefix = options.pop("upload_prefix",
                         cloudinary.config().upload_prefix) or "https://api.cloudinary.com"
    account_id = options.pop("account_id", cloudinary.provisioning.account.account_config().account_id)
    if not account_id:
        raise Exception("Must supply account_id")
    provisioning_api_key = options.pop("api_key", cloudinary.provisioning.account.account_config().provisioning_api_key)
    if not provisioning_api_key:
        raise Exception("Must supply provisioning_api_key")
    provisioning_api_secret = options.pop("api_secret",
                                          cloudinary.provisioning.account.account_config().provisioning_api_secret)
    if not provisioning_api_secret:
        raise Exception("Must supply provisioning_api_secret")
    provisioning_api_url = "/".join(
        [prefix, "v1_1", PROVISIONING_SUB_PATH, ACCOUNT_SUB_PATH, account_id] + uri)

    processed_params = None
    if isinstance(params, dict):
        processed_params = {}
        for key, value in params.items():
            if isinstance(value, list) or isinstance(value, tuple):
                value_list = {"{}[{}]".format(key, i): i_value for i, i_value in enumerate(value)}
                processed_params.update(value_list)
            elif value is not None:
                processed_params[key] = value

    # Add authentication
    req_headers = urllib3.make_headers(
        basic_auth="{0}:{1}".format(provisioning_api_key, provisioning_api_secret),
        user_agent=cloudinary.get_user_agent()
    )
    if headers is not None:
        req_headers.update(headers)
    kw = {}
    if "timeout" in options:
        kw["timeout"] = options["timeout"]
    if body is not None:
        kw["body"] = body
    try:
        response = _http.request(method.upper(), provisioning_api_url, processed_params, req_headers, **kw)
        body = response.data
    except HTTPError as e:
        raise GeneralError("Unexpected error {0}", e.message)
    except socket.error as e:
        raise GeneralError("Socket Error: %s" % (str(e)))

    try:
        result = json.loads(body.decode("utf-8"))
    except Exception as e:
        # Error is parsing json
        raise GeneralError("Error parsing server response (%d) - %s. Got - %s" % (response.status, body, e))

    if "error" in result:
        exception_class = EXCEPTION_CODES.get(response.status) or Exception
        exception_class = exception_class
        raise exception_class("Error {0} - {1}".format(response.status, result["error"]["message"]))

    return result
