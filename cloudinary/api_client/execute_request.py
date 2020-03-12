import json
import socket

from urllib3.exceptions import HTTPError

from cloudinary.exceptions import (
    BadRequest,
    AuthorizationRequired,
    NotAllowed,
    NotFound,
    AlreadyExists,
    RateLimited,
    GeneralError
)
from cloudinary.utils import process_params

EXCEPTION_CODES = {
    400: BadRequest,
    401: AuthorizationRequired,
    403: NotAllowed,
    404: NotFound,
    409: AlreadyExists,
    420: RateLimited,
    500: GeneralError
}


class Response(dict):
    def __init__(self, result, response, **kwargs):
        super(Response, self).__init__(**kwargs)
        self.update(result)


def execute_request(http_connector, method, params, req_headers, api_url, **options):
    processed_params = process_params(params)
    try:
        response = http_connector.request(method.upper(), api_url, processed_params, req_headers, **options)
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
