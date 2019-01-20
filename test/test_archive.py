import tempfile
import time
import unittest
import zipfile

import certifi

import cloudinary
import cloudinary.poster.streaminghttp
from cloudinary import uploader, utils

from mock import patch
import six
import urllib3
from urllib3 import disable_warnings

from test.helper_test import SUFFIX, TEST_IMAGE, api_response_mock, cleanup_test_resources_by_tag

MOCK_RESPONSE = api_response_mock()

TEST_TAG = "arch_pycloudinary_test_{}".format(SUFFIX)
TEST_TAG_RAW = "arch_pycloudinary_test_raw_{}".format(SUFFIX)

disable_warnings()


class ArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        uploader.upload(TEST_IMAGE, tags=[TEST_TAG])
        uploader.upload(TEST_IMAGE, tags=[TEST_TAG], transformation=dict(width=10))

    @classmethod
    def tearDownClass(cls):
        cleanup_test_resources_by_tag([
            (TEST_TAG,),
            (TEST_TAG_RAW, {'resource_type': 'raw'}),
        ])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_archive(self):
        """should successfully generate an archive"""
        result = uploader.create_archive(tags=[TEST_TAG], target_tags=[TEST_TAG_RAW])
        self.assertEqual(2, result.get("file_count"))
        result2 = uploader.create_zip(
            tags=[TEST_TAG], transformations=[{"width": 0.5}, {"width": 2.0}], target_tags=[TEST_TAG_RAW])
        self.assertEqual(4, result2.get("file_count"))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_optional_parameters(self, mocker):
        """should allow optional parameters"""
        mocker.return_value = MOCK_RESPONSE
        expires_at = int(time.time()+3600)
        uploader.create_zip(
            tags=[TEST_TAG],
            expires_at=expires_at,
            allow_missing=True,
            skip_transformation_name=True,
        )
        params = mocker.call_args[0][2]
        self.assertEqual(params['expires_at'], expires_at)
        self.assertTrue(params['allow_missing'])
        self.assertTrue(params['skip_transformation_name'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_archive_url(self):
        result = utils.download_zip_url(tags=[TEST_TAG], transformations=[{"width": 0.5}, {"width": 2.0}])
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where()
        )
        response = http.request('get', result)
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file_name = temp_file.name
            temp_file.write(response.data)
            temp_file.flush()
            with zipfile.ZipFile(temp_file_name, 'r') as zip_file:
                infos = zip_file.infolist()
                self.assertEqual(4, len(infos))
        http.clear()

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_download_zip_url_options(self):
        result = utils.download_zip_url(tags=[TEST_TAG], transformations=[{"width": 0.5}, {"width": 2.0}],
                                        cloud_name="demo")
        upload_prefix = cloudinary.config().upload_prefix or "https://api.cloudinary.com"
        six.assertRegex(self, result, r'^{0}/v1_1/demo/.*$'.format(upload_prefix))


if __name__ == '__main__':
    unittest.main()
