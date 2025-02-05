# -*- coding: latin-1 -*-
import json
import os
import random
import re
import sys
import time
import traceback
import unittest
from contextlib import contextmanager
from datetime import timedelta, tzinfo
from functools import wraps

import six
from urllib3 import HTTPResponse
from urllib3._collections import HTTPHeaderDict
from collections import defaultdict

from cloudinary import utils, logger, api, urlparse
from cloudinary.compat import parse_qsl
from cloudinary.exceptions import NotFound
from test.addon_types import ADDON_ALL

try:
    from unittest import mock
except ImportError:
    # Python 2.7
    import mock

patch = mock.patch

SUFFIX = os.environ.get('TRAVIS_JOB_ID') or random.randint(10000, 99999)

REMOTE_TEST_IMAGE = "http://cloudinary.com/images/old_logo.png"

RESOURCES_PATH = "test/resources/"

TEST_IMAGE = RESOURCES_PATH + "logo.png"
TEST_IMAGE_SIZE = 3381
TEST_UNICODE_IMAGE = RESOURCES_PATH + u"üni_näme_lögö.png"
TEST_DOC = RESOURCES_PATH + "docx.docx"
TEST_ICON = RESOURCES_PATH + "favicon.ico"

TEST_TAG = "pycloudinary_test"
UNIQUE_TAG = "{0}_{1}".format(TEST_TAG, SUFFIX)
UNIQUE_TEST_ID = UNIQUE_TAG
UNIQUE_SUB_ACCOUNT_ID = UNIQUE_TAG
TEST_FOLDER = "test_folder"
UNIQUE_TEST_FOLDER = UNIQUE_TAG + TEST_FOLDER

ZERO = timedelta(0)

EVAL_STR = 'if (resource_info["width"] < 450) { upload_options["quality_analysis"] = true }; ' \
           'upload_options["context"] = "width=" + resource_info["width"]'

ON_SUCCESS_STR = 'current_asset.update({tags: ["autocaption"]});'

try:
    # urllib3 2.x support
    # noinspection PyProtectedMember
    import urllib3._request_methods

    URLLIB3_REQUEST = "urllib3._request_methods.RequestMethods.request"
except ImportError:
    URLLIB3_REQUEST = "urllib3.request.RequestMethods.request"


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


def get_method(mocker):
    return mocker.call_args[1]["method"]


def get_uri(mocker):
    return urlparse(mocker.call_args[1]["url"]).path


def get_headers(mocker):
    return mocker.call_args[1]["headers"]


def get_params_from_url(mocker):
    return parse_query_params(mocker.call_args[1]["url"])


def parse_query_params(url):
    """
    Parses the query parameters from a URL into a dictionary.

    :param url: The URL string to parse.
    :return: Dictionary of query parameters with values as lists.
    """
    parsed_url = urlparse(url)
    query = parsed_url.query
    pairs = parse_qsl(query, keep_blank_values=True)

    params = {}
    list_keys = set()

    for key, value in pairs:
        if key.endswith('[]'):
            key = key[:-2]  # Remove the trailing '[]'
            list_keys.add(key)

        if key in params:
            if key in list_keys:
                params[key].append(value)
            else:
                # If previously a scalar, convert to list
                if isinstance(params[key], list):
                    params[key].append(value)
                else:
                    params[key] = [params[key], value]
        else:
            if key in list_keys:
                params[key] = [value]
            else:
                params[key] = value

    return params


def clean_params(params):
    """
    Cleans the parameter keys by stripping '[]' if present.

    :param params: Dictionary of query parameters with values as lists.
    :return: Cleaned dictionary with bracket-less keys.
    """
    cleaned = {}
    for key, values in params.items():
        if key.endswith('[]'):
            key = key[:-2]  # Remove the trailing '[]'
        cleaned[key] = values
    return cleaned


def get_params(mocker):
    """
    Extracts query parameters from mocked urllib3.request `fields` param.
    Supports both list and dict values of `fields`. Returns params as dictionary.
    Supports two list params formats:
      - {"urls[0]": "http://host1", "urls[1]": "http://host2"}
      - [("urls[]", "http://host1"), ("urls[]", "http://host2")]
    In both cases the result would be {"urls": ["http://host1", "http://host2"]}
    """
    if get_headers(mocker).get("Content-Type", None) == "application/json" and get_method(mocker).upper() != "GET":
        return get_json_body(mocker)
    if get_method(mocker).upper() == "GET":
        return get_params_from_url(mocker)

    if not mocker.call_args[1].get("fields"):
        return {}

    params = {}
    reg = re.compile(r'^(.*)\[\d*]$')
    fields = mocker.call_args[1].get("fields")
    fields = fields.items() if isinstance(fields, dict) else fields
    for k, v in fields:
        match = reg.match(k)
        if match:
            name = match.group(1)
            if name not in params:
                params[name] = []
            params[name].append(v)
        else:
            params[k] = v
    return params


def get_json_body(mocker):
    return json.loads(mocker.call_args[1]["body"].decode('utf-8') or {})


def get_param(mocker, name):
    """
    Return the value of the parameter
    :param mocker: the mocked object
    :param name: the name of the parameter
    :return: the value of the parameter if present or None
    """
    params = get_params(mocker)
    return params.get(name)


def get_list_param(mocker, name):
    """
    Return a list of values for the given param name
    :param mocker: the mocked object
    :param name: the name of the parameter
    :return: a list of values
    """
    return get_param(mocker, name)


def http_response_mock(body="", headers=None, status=200):
    if headers is None:
        headers = {}

    if not six.PY2:
        body = body.encode("UTF-8")

    return HTTPResponse(body, HTTPHeaderDict(headers), status=status)


def api_response_mock(body='{"foo":"bar"}'):
    return http_response_mock(body, {"x-featureratelimit-limit": '0',
                                     "x-featureratelimit-reset": 'Sat, 01 Apr 2017 22:00:00 GMT',
                                     "x-featureratelimit-remaining": '0'})


def uploader_response_mock():
    return http_response_mock('{"foo":"bar"}')


def populate_large_file(file_io, size, chunk_size=4096):
    file_io.write(b"BMJ\xB9Y\x00\x00\x00\x00\x00\x8A\x00\x00\x00|\x00\x00\x00x\x05\x00\x00x\x05\x00\x00\x01\
\x00\x18\x00\x00\x00\x00\x00\xC0\xB8Y\x00a\x0F\x00\x00a\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\
\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFFBGRs\x00\x00\x00\x00\x00\x00\x00\x00T\xB8\x1E\xFC\x00\x00\x00\x00\
\x00\x00\x00\x00fff\xFC\x00\x00\x00\x00\x00\x00\x00\x00\xC4\xF5(\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    remaining_size = size - utils.file_io_size(file_io)

    while remaining_size > 0:
        curr_chunk_size = min(remaining_size, chunk_size)
        file_io.write(b"\xFF" * curr_chunk_size)
        remaining_size -= chunk_size

    file_io.flush()
    file_io.seek(0)


def retry_assertion(num_tries=3, delay=3):
    """
    Helper for retrying inconsistent unit tests

    :param num_tries: Number of tries to perform
    :param delay: Delay in seconds between retries
    """

    def retry_decorator(func):
        @wraps(func)
        def retry_func(*args, **kwargs):
            try_num = 1
            while try_num < num_tries:
                try:
                    return func(*args, **kwargs)
                except AssertionError:
                    logger.warning("Assertion #{} out of {} failed, retrying in {} seconds".format(try_num, num_tries,
                                                                                                   delay))
                    time.sleep(delay)
                    try_num += 1

            return func(*args, **kwargs)

        return retry_func

    return retry_decorator


@contextmanager
def ignore_exception(error_classes=(Exception,), suppress_traceback_classes=()):
    try:
        yield
    except error_classes as e:
        if not isinstance(e, suppress_traceback_classes):
            traceback.print_exc(file=sys.stderr)


def cleanup_test_resources_by_tag(params):
    for tag_with_options in params:
        options = tag_with_options[1] if len(tag_with_options) > 1 else {}
        with ignore_exception():
            api.delete_resources_by_tag(tag_with_options[0], **options)


def cleanup_test_resources(params):
    for public_ids_with_options in params:
        options = public_ids_with_options[1] if len(public_ids_with_options) > 1 else {}
        with ignore_exception():
            api.delete_resources(public_ids_with_options[0], **options)


def cleanup_test_transformation(params):
    for transformations_with_options in params:
        options = transformations_with_options[1] if len(transformations_with_options) > 1 else {}
        for transformation in transformations_with_options[0]:
            with ignore_exception(suppress_traceback_classes=(NotFound,)):
                api.delete_transformation(transformation, **options)


def should_test_addon(addon):
    """
    Checks whether a certain add-on should be tested.
    :param addon: The add-on name.
    :type addon:  str
    :return:      True if that add-on should be tested, False otherwise.
    :rtype:       bool
    """
    cld_test_addons = os.environ.get('CLD_TEST_ADDONS').lower()
    if cld_test_addons == ADDON_ALL:
        return True
    cld_test_addons_list = [addon_name.strip() for addon_name in cld_test_addons.split(',')]
    return addon in cld_test_addons_list


class CldTestCase(unittest.TestCase):
    """
    A custom test case class that extends unittest.TestCase.
    It provides the assertCountEqual method for Python 2.7 compatibility,
    handling unhashable elements by serializing them.
    """

    if six.PY2:
        def assertCountEqual(self, list1, list2, msg=None):
            """
            Fail if two sequences do not contain the same elements the same number of times,
            regardless of their order. Handles unhashable elements by serializing them.
            This is a compatibility method for Python 2.7.
            """

            def serialize_item(item):
                try:
                    # Attempt to serialize the item to a JSON string
                    return json.dumps(item, sort_keys=True)
                except (TypeError, ValueError):
                    # Fallback: use the string representation
                    return str(item)

            def count_elements(lst):
                counts = defaultdict(int)
                for item in lst:
                    serialized = serialize_item(item)
                    counts[serialized] += 1
                return counts

            count1 = count_elements(list1)
            count2 = count_elements(list2)
            if count1 != count2:
                standard_msg = '%s != %s' % (count1, count2)
                self.fail(self._formatMessage(msg, standard_msg))
