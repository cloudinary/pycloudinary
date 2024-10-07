import tempfile
import time
import unittest
import zipfile

import certifi

import cloudinary
import cloudinary.poster.streaminghttp
from cloudinary import uploader, utils

import six
import urllib3
from urllib3 import disable_warnings

from test.helper_test import SUFFIX, TEST_IMAGE, api_response_mock, cleanup_test_resources_by_tag, UNIQUE_TEST_ID, \
    get_uri, get_list_param, get_params, URLLIB3_REQUEST, patch

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

    @patch(URLLIB3_REQUEST)
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
        params = get_params(mocker)
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

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_download_folder(self):
        """Should generate and return a url for downloading a folder"""
        # Should return url with resource_type image
        download_folder_url = utils.download_folder(folder_path="samples/", resource_type="image")
        self.assertIn("image", download_folder_url)

        # Should return valid url
        download_folder_url = utils.download_folder(folder_path="folder/")
        self.assertTrue(download_folder_url)
        self.assertIn("generate_archive", download_folder_url)

        # Should flatten folder
        download_folder_url = utils.download_folder(folder_path="folder/", flatten_folders=True)
        self.assertIn("flatten_folders", download_folder_url)

        # Should expire_at folder
        expiration_time = int(time.time() + 60)
        download_folder_url = utils.download_folder(folder_path="folder/", expires_at=expiration_time)
        self.assertIn("expires_at", download_folder_url)

        # Should use original file_name of folder
        download_folder_url = utils.download_folder(folder_path="folder/", use_original_filename=True)
        self.assertIn("use_original_filename", download_folder_url)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_archive_multiple_resource_types(self, mocker):
        """should allow fully_qualified_public_ids"""

        mocker.return_value = MOCK_RESPONSE

        test_ids = [
            "image/upload/" + UNIQUE_TEST_ID,
            "video/upload/" + UNIQUE_TEST_ID,
            "raw/upload/" + UNIQUE_TEST_ID,
        ]
        uploader.create_zip(
            resource_type='auto',
            fully_qualified_public_ids=test_ids
        )

        self.assertTrue(get_uri(mocker).endswith('/auto/generate_archive'))
        self.assertEqual(test_ids, get_list_param(mocker, 'fully_qualified_public_ids'))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_download_backedup_asset(self):
        download_backedup_asset_url = utils.download_backedup_asset('b71b23d9c89a81a254b88a91a9dad8cd',
                                                                    '0e493356d8a40b856c4863c026891a4e')

        self.assertIn("asset_id", download_backedup_asset_url)
        self.assertIn("version_id", download_backedup_asset_url)


if __name__ == '__main__':
    unittest.main()
