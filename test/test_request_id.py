import unittest

from urllib3 import disable_warnings

import cloudinary
from cloudinary import api, uploader
from cloudinary.exceptions import Error
from test.helper_test import (
    TEST_IMAGE, MOCK_REQUEST_ID, http_response_mock, URLLIB3_REQUEST, patch
)

REQUEST_ID = MOCK_REQUEST_ID

disable_warnings()


class RequestIdTest(unittest.TestCase):
    """
    Covers `request_id` propagation in cases a live server will not produce on demand: a
    missing X-Request-Id header, a malformed body, and a returned rather than raised error.

    The happy paths are covered live, in test_api.py's test_response_metadata for the Admin
    API and test_uploader.py for the Upload API.
    """

    def setUp(self):
        cloudinary.reset_config()
        cloudinary.config(cloud_name="test123", api_key="1234", api_secret="b")

    def tearDown(self):
        cloudinary.reset_config()

    @patch(URLLIB3_REQUEST)
    def test_admin_response_without_request_id(self, mocker):
        """Should leave request_id as None when the header is absent"""
        mocker.return_value = http_response_mock('{"foo":"bar"}')

        self.assertIsNone(api.ping().request_id)

    @patch(URLLIB3_REQUEST)
    def test_upload_response_without_request_id(self, mocker):
        """Should not add a request_id key when the server did not report one"""
        mocker.return_value = http_response_mock('{"public_id":"test"}')

        result = uploader.upload(TEST_IMAGE)

        self.assertNotIn("request_id", result)

    @patch(URLLIB3_REQUEST)
    def test_upload_request_id_is_always_the_header(self, mocker):
        """Should report the X-Request-Id header, which is the transport level identifier

        The Upload API returns no request_id of its own today; if it ever does, the header still
        wins, so the key means one thing consistently.
        """
        mocker.return_value = http_response_mock('{"public_id":"test","request_id":"from_body"}',
                                                 {"x-request-id": REQUEST_ID})

        result = uploader.upload(TEST_IMAGE)

        self.assertEqual(result["request_id"], REQUEST_ID)
        self.assertIs(type(result), dict)

    @patch(URLLIB3_REQUEST)
    def test_upload_parse_error_prints_request_id(self, mocker):
        """Should include the request id in an Upload API parsing error"""
        mocker.return_value = http_response_mock("not json", {"x-request-id": REQUEST_ID},
                                                 status=500)

        with self.assertRaises(Error) as raised:
            uploader.upload(TEST_IMAGE)

        self.assertIn("Request ID: {}".format(REQUEST_ID), str(raised.exception))

    @patch(URLLIB3_REQUEST)
    def test_upload_parse_error_without_request_id_keeps_original_message(self, mocker):
        """Should not add a request id suffix when the response header is absent"""
        mocker.return_value = http_response_mock("not json", status=500)

        with self.assertRaises(Error) as raised:
            uploader.upload(TEST_IMAGE)

        self.assertNotIn("Request ID:", str(raised.exception))

    @patch(URLLIB3_REQUEST)
    def test_upload_returned_error_carries_request_id(self, mocker):
        """Should include the request id when the error is returned rather than raised"""
        mocker.return_value = http_response_mock('{"error":{"message":"bad request"}}',
                                                 {"x-request-id": REQUEST_ID}, status=400)

        result = uploader.upload(TEST_IMAGE, return_error=True)

        self.assertEqual(result["error"]["http_code"], 400)
        self.assertEqual(result["error"]["request_id"], REQUEST_ID)


if __name__ == "__main__":
    unittest.main()
