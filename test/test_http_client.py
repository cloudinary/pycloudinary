from unittest import TestCase

import six

from cloudinary import uploader, HttpClient, GeneralError

import cloudinary
from cloudinary.utils import cloudinary_url

from test.helper_test import UNIQUE_TAG, SUFFIX, TEST_IMAGE, cleanup_test_resources_by_tag

HTTP_CLIENT_UNIQUE_TEST_TAG = 'http_client_{}'.format(UNIQUE_TAG)
HTTP_CLIENT_TEST_ID = "http_client_{}".format(SUFFIX)


class HttpClientTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        if not cloudinary.config().api_secret:
            return
        uploader.upload(TEST_IMAGE, public_id=HTTP_CLIENT_TEST_ID, tags=[HTTP_CLIENT_UNIQUE_TEST_TAG, ])

    @classmethod
    def tearDownClass(cls):
        cleanup_test_resources_by_tag([(HTTP_CLIENT_UNIQUE_TEST_TAG,)])

    def setUp(self):
        cloudinary.reset_config()
        self.http_client = HttpClient()

    def test_http_client_get_json(self):
        json_url = cloudinary_url(HTTP_CLIENT_TEST_ID, width="auto:breakpoints:json")[0]
        json_resp = self.http_client.get_json(json_url)

        self.assertIn("breakpoints", json_resp)
        self.assertIsInstance(json_resp["breakpoints"], list)

    def test_http_client_get_json_non_json(self):
        non_json_url = cloudinary_url(HTTP_CLIENT_TEST_ID)[0]

        with six.assertRaisesRegex(self, GeneralError, "Error parsing server response*"):
            self.http_client.get_json(non_json_url)

    def test_http_client_get_json_invalid_url(self):
        non_existing_url = cloudinary_url(HTTP_CLIENT_TEST_ID + "_non_existing")[0]

        with six.assertRaisesRegex(self, GeneralError, "Server returned unexpected status code*"):
            self.http_client.get_json(non_existing_url)

