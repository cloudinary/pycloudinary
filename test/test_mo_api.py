import unittest
from mock import patch
from urllib3 import disable_warnings

import cloudinary
from cloudinary import mo_api, uploader, utils
from test.helper_test import get_uri, get_method, api_response_mock, get_json_body, TEST_IMAGE
from cloudinary.exceptions import BadRequest, NotFound

MOCK_RESPONSE = api_response_mock()

disable_warnings()


class MoApiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        cloudinary.config(upload_prefix=f"https://{cloudinary.MO_URL}/v1"),
        print("Running tests for cloud: {}".format(cloudinary.config().cloud_name))

    @patch('urllib3.request.RequestMethods.request')
    def test_ping(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        mo_api.ping()
        args, kwargs = mocker.call_args
        uri = get_uri(args)
        *rest, cloud_name, method = uri.rsplit("/", 2)
        self.assertEqual(cloud_name, cloudinary.config().cloud_name)
        self.assertEqual(method, "ping")

    @patch('urllib3.request.RequestMethods.request')
    def test_invalidate(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        mo_api.invalidate(TEST_IMAGE)
        args, kwargs = mocker.call_args
        uri = get_uri(args)
        *rest, cloud_name, method = uri.rsplit("/", 2)
        self.assertEqual(cloud_name, cloudinary.config().cloud_name)
        self.assertEqual(method, "invalidate")
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker)["urls"], [TEST_IMAGE])

    @patch('urllib3.request.RequestMethods.request')
    def test_warm_up(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        mo_api.warm_up(TEST_IMAGE)
        args, kwargs = mocker.call_args
        uri = get_uri(args)
        *rest, cloud_name, method = uri.rsplit("/", 2)
        self.assertEqual(cloud_name, cloudinary.config().cloud_name)
        self.assertEqual(method, "cache_warm_up")
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker)["url"], TEST_IMAGE)

if __name__ == '__main__':
    unittest.main()
