import os
import random

import re

SUFFIX = os.environ.get('TRAVIS_JOB_ID') or random.randint(10000, 99999)
TEST_IMAGE = "tests/logo.png"
TEST_TAG = "pycloudinary_test"
UNIQUE_TAG = "{0}_{1}".format(TEST_TAG, SUFFIX)


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