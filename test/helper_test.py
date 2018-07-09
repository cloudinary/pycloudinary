import os
import random
import re
from datetime import timedelta, tzinfo

import six
from urllib3 import HTTPResponse
from urllib3._collections import HTTPHeaderDict

from cloudinary import utils

SUFFIX = os.environ.get('TRAVIS_JOB_ID') or random.randint(10000, 99999)

REMOTE_TEST_IMAGE = "http://cloudinary.com/images/old_logo.png"

RESOURCES_PATH = "test/resources/"

TEST_IMAGE = RESOURCES_PATH + "logo.png"
TEST_DOC = RESOURCES_PATH + "docx.docx"
TEST_ICON = RESOURCES_PATH + "favicon.ico"

TEST_TAG = "pycloudinary_test"
UNIQUE_TAG = "{0}_{1}".format(TEST_TAG, SUFFIX)

ZERO = timedelta(0)


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


def get_method(mocker):
    return mocker.call_args[0][0]


def get_uri(args):
    return args[1]


def get_params(args):
    return args[2] or {}


def get_param(mocker, name):
    """
    Return the value of the parameter
    :param mocker: the mocked object
    :param name: the name of the paramer
    :return: the value of the parameter if present or None
    """
    args, kargs = mocker.call_args
    params = get_params(args)
    return params.get(name)


def get_list_param(mocker, name):
    """
    Return a list of values for the given param name
    :param mocker: the mocked object
    :param name: the name of the parameter
    :return: a list of values
    """
    args, kargs = mocker.call_args
    params = get_params(args)
    reg = re.compile(r'{}\[\d*\]'.format(name))
    return [params[key] for key in params.keys() if reg.match(key)]


def http_response_mock(body="", headers=None, status=200):
    if headers is None:
        headers = {}

    if not six.PY2:
        body = body.encode("UTF-8")

    return HTTPResponse(body, HTTPHeaderDict(headers), status=status)


def api_response_mock():
    return http_response_mock('{"foo":"bar"}', {"x-featureratelimit-limit": '0',
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
