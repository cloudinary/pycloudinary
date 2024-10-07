import unittest

import six

import cloudinary
from cloudinary import api
from cloudinary import uploader
from test.helper_test import TEST_IMAGE, get_headers, get_params, URLLIB3_REQUEST, patch
from test.test_api import MOCK_RESPONSE
from test.test_config import OAUTH_TOKEN, CLOUD_NAME, API_KEY, API_SECRET
from test.test_uploader import API_TEST_PRESET


class ApiAuthorizationTest(unittest.TestCase):
    def setUp(self):
        self.config = cloudinary.config(cloud_name=CLOUD_NAME, api_key=API_KEY, api_secret=API_SECRET)

    @patch(URLLIB3_REQUEST)
    def test_oauth_token_admin_api(self, mocker):
        self.config.oauth_token = OAUTH_TOKEN
        mocker.return_value = MOCK_RESPONSE

        api.ping()

        headers = get_headers(mocker)

        self.assertTrue("authorization" in headers)
        self.assertEqual("Bearer {}".format(OAUTH_TOKEN), headers["authorization"])

    @patch(URLLIB3_REQUEST)
    def test_oauth_token_as_an_option_admin_api(self, mocker):
        mocker.return_value = MOCK_RESPONSE

        api.ping(oauth_token=OAUTH_TOKEN)

        headers = get_headers(mocker)

        self.assertTrue("authorization" in headers)
        self.assertEqual("Bearer {}".format(OAUTH_TOKEN), headers["authorization"])

    @patch(URLLIB3_REQUEST)
    def test_key_and_secret_admin_api(self, mocker):
        self.config.oauth_token = None
        mocker.return_value = MOCK_RESPONSE

        api.ping()

        headers = get_headers(mocker)

        self.assertTrue("authorization" in headers)
        self.assertEqual("Basic a2V5OnNlY3JldA==", headers["authorization"])

    @patch(URLLIB3_REQUEST)
    def test_missing_credentials_admin_api(self, mocker):
        self.config.oauth_token = None
        self.config.api_key = None
        self.config.api_secret = None

        mocker.return_value = MOCK_RESPONSE

        with six.assertRaisesRegex(self, Exception, "Must supply api_key"):
            api.ping()

    @patch(URLLIB3_REQUEST)
    def test_oauth_token_upload_api(self, mocker):
        self.config.oauth_token = OAUTH_TOKEN
        mocker.return_value = MOCK_RESPONSE

        uploader.upload(TEST_IMAGE)

        headers = get_headers(mocker)

        self.assertTrue("authorization" in headers)
        self.assertEqual("Bearer {}".format(OAUTH_TOKEN), headers["authorization"])

        params = get_params(mocker)
        self.assertNotIn("signature", params)

    @patch(URLLIB3_REQUEST)
    def test_oauth_token_as_an_option_upload_api(self, mocker):
        mocker.return_value = MOCK_RESPONSE

        uploader.upload(TEST_IMAGE, oauth_token=OAUTH_TOKEN)

        headers = get_headers(mocker)

        self.assertTrue("authorization" in headers)
        self.assertEqual("Bearer {}".format(OAUTH_TOKEN), headers["authorization"])

    @patch(URLLIB3_REQUEST)
    def test_key_and_secret_upload_api(self, mocker):
        self.config.oauth_token = None
        mocker.return_value = MOCK_RESPONSE

        uploader.upload(TEST_IMAGE)

        headers = get_headers(mocker)
        self.assertNotIn("authorization", headers)

        params = get_params(mocker)
        self.assertIn("signature", params)
        self.assertIn("api_key", params)

    @patch(URLLIB3_REQUEST)
    def test_missing_credentials_upload_api(self, mocker):
        self.config.oauth_token = None
        self.config.api_key = None
        self.config.api_secret = None

        mocker.return_value = MOCK_RESPONSE

        with six.assertRaisesRegex(self, Exception, "Must supply api_key"):
            uploader.upload(TEST_IMAGE)

        # no credentials required for unsigned upload
        uploader.unsigned_upload(TEST_IMAGE, upload_preset=API_TEST_PRESET)

        args, _ = mocker.call_args
        params = get_params(mocker)
        self.assertTrue("upload_preset" in params)


if __name__ == '__main__':
    unittest.main()
