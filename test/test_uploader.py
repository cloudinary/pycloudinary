import io
import os
import tempfile
import unittest
from collections import OrderedDict
from datetime import datetime

import six
from urllib3 import disable_warnings

import cloudinary
from cloudinary import api, uploader, utils, exceptions
from cloudinary.cache import responsive_breakpoints_cache
from cloudinary.cache.adapter.key_value_cache_adapter import KeyValueCacheAdapter
from cloudinary.compat import urlparse, parse_qs
from test.cache.storage.dummy_cache_storage import DummyCacheStorage
from test.helper_test import uploader_response_mock, SUFFIX, TEST_IMAGE, get_params, get_headers, TEST_ICON, TEST_DOC, \
    REMOTE_TEST_IMAGE, UTC, populate_large_file, TEST_UNICODE_IMAGE, get_uri, get_method, get_param, \
    cleanup_test_resources_by_tag, cleanup_test_transformation, cleanup_test_resources, EVAL_STR, ON_SUCCESS_STR, \
    URLLIB3_REQUEST, patch, retry_assertion, CldTestCase
from test.test_utils import TEST_ID, TEST_FOLDER

MOCK_RESPONSE = uploader_response_mock()

TEST_IMAGE_HEIGHT = 51
TEST_IMAGE_WIDTH = 241

TEST_TRANS_OVERLAY = {"font_family": "arial", "font_size": 20, "text": SUFFIX}
TEST_TRANS_OVERLAY_STR = "text:arial_20:{}".format(SUFFIX)

TEST_TRANS_SCALE2 = dict(crop="scale", width="2.0", overlay=TEST_TRANS_OVERLAY_STR)
TEST_TRANS_SCALE2_STR = "c_scale,l_{},w_2.0".format(TEST_TRANS_OVERLAY_STR)

TEST_TRANS_SCALE2_PNG = dict(crop="scale", width="2.0", format="png", overlay=TEST_TRANS_OVERLAY_STR)
TEST_TRANS_SCALE2_PNG_STR = "c_scale,l_{},w_2.0/png".format(TEST_TRANS_OVERLAY_STR)

UNIQUE_TAG = "up_test_uploader_{}".format(SUFFIX)
UNIQUE_ID = UNIQUE_TAG
TEST_DOCX_ID = "test_docx_{}".format(SUFFIX)
TEXT_ID = "text_{}".format(SUFFIX)
TEST_ID1 = "uploader_test_{}".format(SUFFIX)
TEST_ID2 = "uploader_test_{}2".format(SUFFIX)
API_TEST_PRESET = "api_test_upload_preset"

LARGE_FILE_SIZE = 5880138
LARGE_CHUNK_SIZE = 5243000
LARGE_FILE_WIDTH = 1400
LARGE_FILE_HEIGHT = 1400

METADATA_FIELD_UNIQUE_EXTERNAL_ID = 'metadata_field_external_id_{}'.format(UNIQUE_ID)
METADATA_FIELD_VALUE = 'metadata_field_value_{}'.format(UNIQUE_ID)

DATASOURCE_ENTRY_1 = "metadata_datasource_entry_external_id_1_{}".format(UNIQUE_ID)
DATASOURCE_ENTRY_2 = "metadata_datasource_entry_external_id_2_{}".format(UNIQUE_ID)

METADATA_FIELD_EXTERNAL_ID_SET = "metadata_upload_external_id_set_{}".format(UNIQUE_ID)
METADATA_FIELD_SET_DATASOURCE_MULTIPLE = [
    {
        "value": "v1",
        "external_id": DATASOURCE_ENTRY_1,
    },
    {
        "value": "v2",
        "external_id": DATASOURCE_ENTRY_2,
    }
]

METADATA_FIELDS = {
    METADATA_FIELD_UNIQUE_EXTERNAL_ID: METADATA_FIELD_VALUE,
    METADATA_FIELD_EXTERNAL_ID_SET: [DATASOURCE_ENTRY_1, DATASOURCE_ENTRY_2]
}

FD_PID_PREFIX = "fd_public_id_prefix"
ASSET_FOLDER = "asset_folder"
DISPLAY_NAME = "test"

disable_warnings()


class UploaderTest(CldTestCase):
    rbp_trans = {"angle": 45, "crop": "scale"}
    rbp_format = "png"
    rbp_values = [206, 50]
    rbp_params = {
        "use_cache": True,
        "responsive_breakpoints":
            [
                {
                    "create_derived": False,
                    "transformation":
                        {
                            "angle": 90
                        },
                    "format": "gif"
                },
                {
                    "create_derived": False,
                    "transformation": rbp_trans,
                    "format": rbp_format
                },
                {
                    "create_derived": False
                }
            ],
        "type": "upload"
    }

    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        if not cloudinary.config().api_secret:
            return

        print("Running tests for cloud: {}".format(cloudinary.config().cloud_name))

        api.add_metadata_field({
            "external_id": METADATA_FIELD_UNIQUE_EXTERNAL_ID,
            "label": METADATA_FIELD_UNIQUE_EXTERNAL_ID,
            "type": "string",
        })

        api.add_metadata_field({
            "external_id": METADATA_FIELD_EXTERNAL_ID_SET,
            "label": METADATA_FIELD_EXTERNAL_ID_SET,
            "type": "set",
            "datasource": {
                "values": METADATA_FIELD_SET_DATASOURCE_MULTIPLE,
            },
        })

    def setUp(self):
        cloudinary.reset_config()

    @classmethod
    def tearDownClass(cls):
        cleanup_test_resources_by_tag([
            (UNIQUE_TAG,),
            (UNIQUE_TAG, {'resource_type': 'raw'}),
            (UNIQUE_TAG, {'type': 'twitter_name'}),
        ])

        cleanup_test_resources([
            ([TEST_ID1, TEST_ID2],),
            ([TEXT_ID], {'type': 'text'}),
            ([TEST_DOCX_ID], {'resource_type': 'raw'}),
        ])

        cleanup_test_transformation([
            ([TEST_TRANS_SCALE2_STR, TEST_TRANS_SCALE2_PNG_STR],),
        ])

        api.delete_metadata_field(METADATA_FIELD_UNIQUE_EXTERNAL_ID)
        api.delete_metadata_field(METADATA_FIELD_EXTERNAL_ID_SET)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload(self):
        """Should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

        # Test upload with metadata
        result = uploader.upload(TEST_IMAGE, metadata=METADATA_FIELDS, tags=[UNIQUE_TAG])
        self.assertIn(METADATA_FIELD_UNIQUE_EXTERNAL_ID, result['metadata'])
        self.assertEqual(result['metadata'].get(METADATA_FIELD_UNIQUE_EXTERNAL_ID), METADATA_FIELD_VALUE)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_path_lib_path(self):
        """Should successfully upload a pathlib.Path file object"""
        try:
            import pathlib
        except ImportError:
            self.skipTest("pathlib is not supported")
            return

        path_lib_image_path = pathlib.Path(TEST_IMAGE)

        result = uploader.upload(path_lib_image_path, tags=[UNIQUE_TAG])

        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(path_lib_image_path.stem, result["original_filename"])

        result = uploader.upload_large(path_lib_image_path, tags=[UNIQUE_TAG], resource_type="image")

        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_unicode_filename(self):
        """Should successfully upload file with unicode characters"""
        expected_name = os.path.splitext(os.path.basename(TEST_UNICODE_IMAGE))[0]

        result = uploader.upload(TEST_UNICODE_IMAGE, tags=[UNIQUE_TAG], use_filename=True, unique_filename=False)

        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)

        self.assertEqual(expected_name, result["public_id"])
        self.assertEqual(expected_name, result["original_filename"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_file_io_without_filename(self):
        """Should successfully upload FileIO file """
        with io.BytesIO() as temp_file, open(TEST_IMAGE, 'rb') as input_file:
            temp_file.write(input_file.read())
            temp_file.seek(0)

            result = uploader.upload(temp_file, tags=[UNIQUE_TAG])

        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        self.assertEqual('stream', result["original_filename"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_custom_filename(self):
        """Should successfully use custom filename regardless actual file path"""

        custom_filename = UNIQUE_ID + "_" + os.path.basename(TEST_IMAGE)

        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], filename=custom_filename)

        self.assertEqual(os.path.splitext(custom_filename)[0], result["original_filename"])

        with io.BytesIO() as temp_file, open(TEST_IMAGE, 'rb') as input_file:
            temp_file.write(input_file.read())
            temp_file.seek(0)

            result = uploader.upload(temp_file, tags=[UNIQUE_TAG], filename=custom_filename)

        self.assertEqual(os.path.splitext(custom_filename)[0], result["original_filename"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_filename_override(self):
        """should successfully override original_filename"""

        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], filename_override='overridden')

        self.assertEqual('overridden', result["original_filename"])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_async(self, mocker):
        """Should pass async value """
        mocker.return_value = MOCK_RESPONSE
        async_option = {"async": True}
        uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], **async_option)
        self.assertTrue(get_param(mocker, 'async'))

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_folder_decoupling(self, mocker):
        """Should pass folder decoupling params """
        mocker.return_value = MOCK_RESPONSE

        fd_params = {"public_id_prefix": FD_PID_PREFIX, "asset_folder": ASSET_FOLDER, "display_name": DISPLAY_NAME,
                     "use_filename_as_display_name": True, "folder": TEST_FOLDER,
                     "use_asset_folder_as_public_id_prefix": True}
        uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], **fd_params)

        self.assertEqual(FD_PID_PREFIX, get_param(mocker, "public_id_prefix"))
        self.assertEqual(ASSET_FOLDER, get_param(mocker, "asset_folder"))
        self.assertEqual(DISPLAY_NAME, get_param(mocker, "display_name"))
        self.assertEqual("1", get_param(mocker, "use_filename_as_display_name"))
        self.assertEqual("1", get_param(mocker, "use_asset_folder_as_public_id_prefix"))
        self.assertEqual(TEST_FOLDER, get_param(mocker, "folder"))

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_ocr(self, mocker):
        """Should pass ocr value """
        mocker.return_value = MOCK_RESPONSE
        uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], ocr='adv_ocr')

        self.assertEqual(get_params(mocker)['ocr'], 'adv_ocr')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_quality_analysis(self):
        """Should return quality analysis information """
        result = uploader.upload(
            TEST_IMAGE,
            tags=[UNIQUE_TAG],
            quality_analysis=True)

        self.assertIn("quality_analysis", result)
        self.assertIn("focus", result["quality_analysis"])
        self.assertIsInstance(result["quality_analysis"]["focus"], float)

        result = uploader.explicit(
            result["public_id"],
            type="upload",
            tags=[UNIQUE_TAG],
            quality_analysis=True)

        self.assertIn("quality_analysis", result)
        self.assertIn("focus", result["quality_analysis"])
        self.assertIsInstance(result["quality_analysis"]["focus"], float)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_quality_override(self, mocker):
        """Should pass quality_override """
        mocker.return_value = MOCK_RESPONSE
        test_values = ['auto:advanced', 'auto:best', '80:420', 'none']
        for quality in test_values:
            uploader.upload(TEST_IMAGE, tags=UNIQUE_TAG, quality_override=quality)
            quality_override = get_param(mocker, 'quality_override')
            self.assertEqual(quality_override, quality)
        # verify explicit works too
        uploader.explicit(TEST_IMAGE, quality_override='auto:best')
        quality_override = get_param(mocker, 'quality_override')
        self.assertEqual(quality_override, 'auto:best')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_url(self):
        """Should successfully upload file by url """
        result = uploader.upload(REMOTE_TEST_IMAGE, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_unicode_url(self):
        """Should successfully upload file by unicode url """
        unicode_image_url = u"{}".format(REMOTE_TEST_IMAGE)
        result = uploader.upload(unicode_image_url, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_data_uri(self):
        """Should successfully upload file by data url """
        result = uploader.upload(
            u"""\
data:image/png;base64,iVBORw0KGgoAA
AANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABlBMVEUAAAD///+l2Z/dAAAAM0l
EQVR4nGP4/5/h/1+G/58ZDrAz3D/McH8yw83NDDeNGe4Ug9C9zwz3gVLMDA/A6
P9/AFGGFyjOXZtQAAAAAElFTkSuQmCC\
""",
            tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], 16)
        self.assertEqual(result["height"], 16)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_responsive_breakpoints_cache(self):
        """Should save responsive breakpoints to cache after upload"""
        cache = responsive_breakpoints_cache.instance
        cache.set_cache_adapter(KeyValueCacheAdapter(DummyCacheStorage()))

        upload_result = uploader.upload(TEST_IMAGE, **self.rbp_params)

        cache_value = cache.get(upload_result["public_id"], transformation=self.rbp_trans, format=self.rbp_format)

        self.assertEqual(self.rbp_values, cache_value)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename(self):
        """Should successfully rename a file"""
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        uploader.rename(result["public_id"], result["public_id"] + "2")
        self.assertIsNotNone(api.resource(result["public_id"] + "2"))
        result2 = uploader.upload(TEST_ICON, tags=[UNIQUE_TAG])
        self.assertRaises(exceptions.Error, uploader.rename,
                          result2["public_id"], result["public_id"] + "2")
        uploader.rename(result2["public_id"], result["public_id"] + "2", overwrite=True)
        self.assertEqual(api.resource(result["public_id"] + "2")["format"], "ico")

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename_parameters(self, mocker):
        """Should support to_type, invalidate, and overwrite """
        mocker.return_value = MOCK_RESPONSE
        uploader.rename(TEST_IMAGE, TEST_IMAGE + "2", to_type='raw', invalidate=True, overwrite=False)

        self.assertEqual(get_params(mocker)['to_type'], 'raw')
        self.assertTrue(get_params(mocker)['invalidate'])
        self.assertTrue(get_params(mocker)['overwrite'])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename_supports_context(self, mocker):
        """Should support context"""
        mocker.return_value = MOCK_RESPONSE

        uploader.rename(TEST_IMAGE, TEST_IMAGE + "2", context=True)

        self.assertTrue(get_params(mocker)['context'])

        uploader.rename(TEST_IMAGE, TEST_IMAGE + "2")

        self.assertIsNone(get_params(mocker).get('context'))

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename_supports_metadata(self, mocker):
        """Should support metadata"""
        mocker.return_value = MOCK_RESPONSE

        uploader.rename(TEST_IMAGE, TEST_IMAGE + "2", metadata=True)

        self.assertTrue(get_params(mocker)['metadata'])

        uploader.rename(TEST_IMAGE, TEST_IMAGE + "2")

        self.assertIsNone(get_params(mocker).get('metadata'))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_use_filename(self):
        """Should successfully take use file name of uploaded file in public id if specified use_filename """
        result = uploader.upload(TEST_IMAGE, use_filename=True, tags=[UNIQUE_TAG])
        six.assertRegex(self, result["public_id"], 'logo_[a-z0-9]{6}')
        result = uploader.upload(TEST_IMAGE, use_filename=True, unique_filename=False, tags=[UNIQUE_TAG])
        self.assertEqual(result["public_id"], 'logo')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_explicit(self):
        # Test explicit with metadata
        resource = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result_metadata = uploader.explicit(resource['public_id'], type="upload", metadata=METADATA_FIELDS,
                                            tags=[UNIQUE_TAG])
        self.assertIn(METADATA_FIELD_UNIQUE_EXTERNAL_ID, result_metadata['metadata'])
        self.assertEqual(result_metadata['metadata'].get(METADATA_FIELD_UNIQUE_EXTERNAL_ID), METADATA_FIELD_VALUE)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_explicit_responsive_breakpoints_cache(self):
        """Should save responsive breakpoints to cache after explicit"""
        cache = responsive_breakpoints_cache.instance
        cache.set_cache_adapter(KeyValueCacheAdapter(DummyCacheStorage()))

        upload_result = uploader.upload(TEST_IMAGE)
        explicit_result = uploader.explicit(upload_result["public_id"], **self.rbp_params)

        cache_value = cache.get(explicit_result["public_id"], transformation=self.rbp_trans, format=self.rbp_format)

        self.assertEqual(self.rbp_values, cache_value)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_update_metadata(self):
        metadata = {METADATA_FIELD_UNIQUE_EXTERNAL_ID: "test"}
        test_image = uploader.upload(TEST_IMAGE, metadata=metadata, tags=[UNIQUE_TAG])
        public_ids = [test_image['public_id']]

        result = uploader.update_metadata(METADATA_FIELDS, public_ids)

        self.assertEqual(result, {
            "public_ids": public_ids,
        })

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_clear_invalid(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        uploader.update_metadata(METADATA_FIELDS, public_ids=[TEST_ID], clear_invalid=True)
        self.assertTrue(get_param(mocker, "clear_invalid"))

    def test_upload_with_metadata(self):
        """Upload should support `metadata` parameter"""
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], metadata=METADATA_FIELDS)
        self.assertEqual(METADATA_FIELD_VALUE, result['metadata'][METADATA_FIELD_UNIQUE_EXTERNAL_ID])

    def test_explicit_with_metadata(self):
        """Explicit should support `metadata` parameter"""
        resource = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result = uploader.explicit(resource['public_id'], type="upload", metadata=METADATA_FIELDS)
        self.assertEqual(METADATA_FIELD_VALUE, result['metadata'][METADATA_FIELD_UNIQUE_EXTERNAL_ID])

    def test_uploader_update_metadata(self):
        """Should edit metadata of an existing resource"""
        resource = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result = uploader.update_metadata(METADATA_FIELDS, resource['public_id'])
        self.assertEqual(len(result['public_ids']), 1)
        self.assertIn(resource['public_id'], result['public_ids'])

    def test_uploader_update_metadata_on_multiple_resources(self):
        """Should edit metadata of multiple existing resources"""
        resource1 = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        resource2 = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result = uploader.update_metadata(METADATA_FIELDS, [
            resource1['public_id'],
            resource2['public_id']
        ])
        self.assertEqual(len(result['public_ids']), 2)
        self.assertIn(resource1['public_id'], result['public_ids'])
        self.assertIn(resource2['public_id'], result['public_ids'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_eager(self):
        """Should support eager """
        uploader.upload(TEST_IMAGE, eager=[TEST_TRANS_SCALE2], tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_header(self):
        """Should support headers """
        uploader.upload(TEST_IMAGE, headers=["Link: 1"], tags=[UNIQUE_TAG])
        uploader.upload(TEST_IMAGE, headers={"Link": "1"}, tags=[UNIQUE_TAG])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_extra_headers(self, mocker):
        """Should support extra headers"""
        mocker.return_value = MOCK_RESPONSE
        uploader.upload(TEST_IMAGE, extra_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                 'Chrome/58.0.3029.110 Safari/537.3'})
        headers = get_headers(mocker)
        self.assertEqual(headers.get('User-Agent'), 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                    'Chrome/58.0.3029.110 Safari/537.3')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_text(self):
        """Should successfully generate text image """
        result = uploader.text("hello world", public_id=TEXT_ID)
        self.assertGreater(result["width"], 1)
        self.assertGreater(result["height"], 1)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_slideshow_from_manifest_transformation(self, mocker):
        """Should create slideshow from a manifest transformation"""
        mocker.return_value = MOCK_RESPONSE

        slideshow_manifest = "w_352;h_240;du_5;fps_30;vars_(slides_((media_s64:aHR0cHM6Ly9y" + \
                             "ZXMuY2xvdWRpbmFyeS5jb20vZGVtby9pbWFnZS91cGxvYWQvY291cGxl);(media_s64:aH" + \
                             "R0cHM6Ly9yZXMuY2xvdWRpbmFyeS5jb20vZGVtby9pbWFnZS91cGxvYWQvc2FtcGxl)))"

        uploader.create_slideshow(
            manifest_transformation={
                "custom_function": {
                    "function_type": "render",
                    "source": slideshow_manifest,
                }
            },
            transformation={"fetch_format": "auto", "quality": "auto"},
            tags=['tag1', 'tag2', 'tag3']
        )

        args, _ = mocker.call_args

        self.assertTrue(get_uri(mocker).endswith('/video/create_slideshow'))

        self.assertEqual("fn_render:" + slideshow_manifest, get_params(mocker)['manifest_transformation'])
        self.assertEqual("f_auto,q_auto", get_params(mocker)['transformation'])
        self.assertEqual("tag1,tag2,tag3", get_params(mocker)['tags'])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_slideshow_from_manifest_json(self, mocker):
        """Should create slideshow from a manifest json"""
        mocker.return_value = MOCK_RESPONSE
        slideshow_manifest_json = OrderedDict((
            ("w", 848),
            ("h", 480),
            ("du", 6),
            ("fps", 30),
            ("vars", OrderedDict((
                ("sdur", 500),
                ("tdur", 500),
                ("slides", [
                    {"media": "i:protests9"},
                    {"media": "i:protests8"},
                    {"media": "i:protests7"},
                    {"media": "i:protests6"},
                    {"media": "i:protests2"},
                    {"media": "i:protests1"}
                ])
            )))
        ))

        slideshow_manifest_json_str = '{"w":848,"h":480,"du":6,"fps":30,"vars":{"sdur":500,"tdur":500,' + \
                                      '"slides":[{"media":"i:protests9"},{"media":"i:protests8"},' + \
                                      '{"media":"i:protests7"},{"media":"i:protests6"},{"media":"i:protests2"},' + \
                                      '{"media":"i:protests1"}]}}'
        notification_url = "https://example.com"

        uploader.create_slideshow(
            manifest_json=slideshow_manifest_json,
            overwrite=True,
            public_id=TEST_ID,
            notification_url=notification_url,
            upload_preset=API_TEST_PRESET
        )

        args, _ = mocker.call_args

        self.assertEqual(slideshow_manifest_json_str, get_params(mocker)["manifest_json"])
        self.assertEqual("1", get_params(mocker)["overwrite"])
        self.assertEqual(TEST_ID, get_params(mocker)["public_id"])
        self.assertEqual(notification_url, get_params(mocker)["notification_url"])
        self.assertEqual(API_TEST_PRESET, get_params(mocker)["upload_preset"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_tags(self):
        """Should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result2 = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        uploader.add_tag("tag1", [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag2", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag1", "tag2", UNIQUE_TAG])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1", UNIQUE_TAG])
        uploader.remove_tag("tag1", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag2", UNIQUE_TAG])
        uploader.replace_tag("tag3", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag3"])
        uploader.replace_tag(UNIQUE_TAG, result["public_id"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @retry_assertion()
    def test_multiple_tags(self):
        """ Should support adding multiple tags: list ["tag1","tag2"] and comma-separated "tag1,tag2" """
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result2 = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])

        uploader.add_tag(["tag1", "tag2"], [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag3,tag4", [result["public_id"], result2["public_id"]])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag1", "tag2", "tag3", "tag4", UNIQUE_TAG])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1", "tag2", "tag3", "tag4", UNIQUE_TAG])

        uploader.remove_tag(["tag1", "tag2"], result["public_id"])
        uploader.remove_tag("tag3,tag4", result2["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag3", "tag4", UNIQUE_TAG])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1", "tag2", UNIQUE_TAG])

        uploader.replace_tag(["tag5", UNIQUE_TAG], result["public_id"])
        uploader.replace_tag("tag7," + UNIQUE_TAG, result2["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag5", UNIQUE_TAG])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag7", UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_remove_all_tags(self):
        """Should successfully remove all tags"""
        result = uploader.upload(TEST_IMAGE, public_id=TEST_ID1)
        result2 = uploader.upload(TEST_IMAGE, public_id=TEST_ID2)
        uploader.add_tag("tag1", [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag2", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag1", "tag2"])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1"])
        uploader.remove_all_tags([result["public_id"], result2["public_id"]])
        self.assertFalse("tags" in api.resource(result["public_id"]))
        self.assertFalse("tags" in api.resource(result2["public_id"]))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats(self):
        """Should allow whitelisted formats if allowed_formats """
        result = uploader.upload(TEST_IMAGE, allowed_formats=['png'], tags=[UNIQUE_TAG])
        self.assertEqual(result["format"], "png")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_illegal_format(self):
        """Should prevent non whitelisted formats from being uploaded if allowed_formats is specified"""
        self.assertRaises(exceptions.Error, uploader.upload, TEST_IMAGE, allowed_formats=['jpg'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_format(self):
        """Should allow non whitelisted formats if type is specified and convert to that type"""
        result = uploader.upload(TEST_IMAGE, allowed_formats=['jpg'], format='jpg', tags=[UNIQUE_TAG])
        self.assertEqual("jpg", result["format"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_face_coordinates(self):
        """Should allow sending face coordinates"""
        coordinates = [[120, 30, 109, 150], [121, 31, 110, 151]]
        result_coordinates = [[120, 30, 109, 51], [121, 31, 110, 51]]
        result = uploader.upload(TEST_IMAGE, face_coordinates=coordinates,
                                 faces=True, tags=[UNIQUE_TAG])
        self.assertEqual(result_coordinates, result["faces"])

        different_coordinates = [[122, 32, 111, 152]]
        custom_coordinates = [1, 2, 3, 4]
        uploader.explicit(result["public_id"], face_coordinates=different_coordinates,
                          custom_coordinates=custom_coordinates, type="upload")
        info = api.resource(result["public_id"], faces=True, coordinates=True)
        self.assertEqual(different_coordinates, info["faces"])
        self.assertEqual({"faces": different_coordinates, "custom": [custom_coordinates]}, info["coordinates"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_context(self):
        """Should allow sending context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, context=context, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_add_context(self):
        """Should allow adding context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertFalse("context" in info)
        uploader.add_context(context, result["public_id"])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_remove_all_context(self):
        """Should allow removing all context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, context=context, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])
        uploader.remove_all_context(result["public_id"])
        info = api.resource(result["public_id"], context=True)
        self.assertFalse("context" in info)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_manual_moderation(self):
        """Should support setting manual moderation status """
        resource = uploader.upload(TEST_IMAGE, moderation="manual", tags=[UNIQUE_TAG])

        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_raw_conversion(self):
        """Should support requesting raw_convert """
        with six.assertRaisesRegex(self, exceptions.Error, 'Raw convert is invalid'):
            uploader.upload(TEST_DOC, public_id=TEST_DOCX_ID, raw_convert="illegal",
                            resource_type="raw", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_categorization(self):
        """Should support requesting categorization """
        with six.assertRaisesRegex(self, exceptions.Error, 'is not valid'):
            uploader.upload(TEST_IMAGE, categorization="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_detection(self):
        """Should support requesting detection """
        with six.assertRaisesRegex(self, exceptions.Error, "Detection invalid model 'illegal'"):
            uploader.upload(TEST_IMAGE, detection="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large(self):
        """Should support uploading large files """
        filename = UNIQUE_ID + "_cld_upload_large"
        with tempfile.NamedTemporaryFile(prefix=filename, suffix='.bmp') as temp_file:
            populate_large_file(temp_file, LARGE_FILE_SIZE)
            temp_file_name = temp_file.name
            temp_file_filename = os.path.splitext(os.path.basename(temp_file_name))[0]

            self.assertEqual(LARGE_FILE_SIZE, os.path.getsize(temp_file_name))

            resource = uploader.upload_large(temp_file_name, chunk_size=LARGE_CHUNK_SIZE,
                                             tags=["upload_large_tag", UNIQUE_TAG])

            self.assertCountEqual(resource["tags"], ["upload_large_tag", UNIQUE_TAG])
            self.assertEqual(resource["resource_type"], "raw")
            self.assertEqual(resource["original_filename"], temp_file_filename)

            resource2 = uploader.upload_large(temp_file_name, chunk_size=LARGE_CHUNK_SIZE,
                                              tags=["upload_large_tag", UNIQUE_TAG], resource_type="image",
                                              use_filename=True, unique_filename=False, filename=filename)

            self.assertCountEqual(resource2["tags"], ["upload_large_tag", UNIQUE_TAG])
            self.assertEqual(resource2["resource_type"], "image")
            self.assertEqual(resource2["original_filename"], filename)
            self.assertEqual(resource2["original_filename"], resource2["public_id"])
            self.assertEqual(resource2["width"], LARGE_FILE_WIDTH)
            self.assertEqual(resource2["height"], LARGE_FILE_HEIGHT)

            resource3 = uploader.upload_large(temp_file_name, chunk_size=LARGE_FILE_SIZE,
                                              tags=["upload_large_tag", UNIQUE_TAG])

            self.assertCountEqual(resource3["tags"], ["upload_large_tag", UNIQUE_TAG])
            self.assertEqual(resource3["resource_type"], "raw")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large_url(self):
        """Should allow fallback of upload large with remote url to regular upload"""
        resource4 = uploader.upload_large(REMOTE_TEST_IMAGE, tags=[UNIQUE_TAG])

        self.assertEqual(resource4["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(resource4["height"], TEST_IMAGE_HEIGHT)

        expected_signature = utils.api_sign_request(
            dict(public_id=resource4["public_id"], version=resource4["version"]), cloudinary.config().api_secret)

        self.assertEqual(resource4["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large_file_io(self):
        """Should support uploading large streams"""
        with io.BytesIO() as temp_file:
            populate_large_file(temp_file, LARGE_FILE_SIZE)
            resource = uploader.upload_large(temp_file, chunk_size=LARGE_CHUNK_SIZE,
                                             tags=["upload_large_tag", UNIQUE_TAG], resource_type="image")

            self.assertEqual(resource["tags"], ["upload_large_tag", UNIQUE_TAG])
            self.assertEqual(resource["resource_type"], "image")
            self.assertEqual(resource["width"], LARGE_FILE_WIDTH)
            self.assertEqual(resource["height"], LARGE_FILE_HEIGHT)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_preset(self, mocker):
        """Should support unsigned uploading using presets """
        mocker.return_value = MOCK_RESPONSE

        uploader.unsigned_upload(TEST_IMAGE, API_TEST_PRESET)

        self.assertTrue(get_uri(mocker).endswith("/image/upload"))
        self.assertEqual("POST", get_method(mocker))
        self.assertIsNotNone(get_param(mocker, "file"))
        self.assertIsNone(get_param(mocker, "signature"))
        self.assertEqual(get_param(mocker, "upload_preset"), API_TEST_PRESET)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_preset_in_config(self, mocker):
        """Should support uploading using presets from config"""
        mocker.return_value = MOCK_RESPONSE
        cloudinary.config().upload_preset = API_TEST_PRESET
        uploader.upload(TEST_IMAGE)

        self.assertTrue(get_uri(mocker).endswith("/image/upload"))
        self.assertEqual("POST", get_method(mocker))
        self.assertIsNotNone(get_param(mocker, "file"))
        self.assertEqual(get_param(mocker, "upload_preset"), API_TEST_PRESET)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test1_upload_preset_in_config(self, mocker):
        """Should support overwriting upload presets in config"""
        mocker.return_value = MOCK_RESPONSE
        cloudinary.config().upload_preset = API_TEST_PRESET
        uploader.upload(TEST_IMAGE, upload_preset=None)

        self.assertTrue(get_uri(mocker).endswith("/image/upload"))
        self.assertEqual("POST", get_method(mocker))
        self.assertIsNotNone(get_param(mocker, "file"))
        self.assertEqual(get_param(mocker, "upload_preset"), None)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_background_removal(self):
        """Should support requesting background_removal """
        with six.assertRaisesRegex(self, exceptions.Error, 'is invalid'):
            uploader.upload(TEST_IMAGE, background_removal="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_timeout(self):
        with six.assertRaisesRegex(self, exceptions.Error, 'timed out'):
            uploader.upload(TEST_IMAGE, timeout=0.001, tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_responsive_breakpoints(self):
        result = uploader.upload(
            TEST_IMAGE,
            tags=[UNIQUE_TAG],
            responsive_breakpoints=dict(create_derived=False,
                                        transformation=dict(angle=90)))

        self.assertIsNotNone(result["responsive_breakpoints"])
        self.assertEqual(result["responsive_breakpoints"][0]["transformation"],
                         "a_90")

        result = uploader.explicit(
            result["public_id"],
            type="upload",
            tags=[UNIQUE_TAG],
            responsive_breakpoints=[dict(create_derived=False,
                                         transformation=dict(angle=90)),
                                    dict(create_derived=False,
                                         transformation=dict(angle=45))])

        self.assertIsNotNone(result["responsive_breakpoints"])
        self.assertEqual(result["responsive_breakpoints"][0]["transformation"],
                         "a_90")
        self.assertEqual(result["responsive_breakpoints"][1]["transformation"],
                         "a_45")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @patch(URLLIB3_REQUEST)
    def test_access_control(self, request_mock):
        request_mock.return_value = MOCK_RESPONSE

        # Should accept a dictionary of strings
        acl = OrderedDict((("access_type", "anonymous"),
                           ("start", "2018-02-22 16:20:57 +0200"),
                           ("end", "2018-03-22 00:00 +0200")))
        exp_acl = '[{"access_type":"anonymous","start":"2018-02-22 16:20:57 +0200","end":"2018-03-22 00:00 +0200"}]'

        uploader.upload(TEST_IMAGE, access_control=acl)
        params = get_params(request_mock)

        self.assertIn("access_control", params)
        self.assertEqual(exp_acl, params["access_control"])

        # Should accept a dictionary of datetime objects
        acl_2 = OrderedDict((("access_type", "anonymous"),
                             ("start", datetime.strptime("2019-02-22 16:20:57Z", "%Y-%m-%d %H:%M:%SZ")),
                             ("end", datetime(2019, 3, 22, 0, 0, tzinfo=UTC()))))

        exp_acl_2 = '[{"access_type":"anonymous","start":"2019-02-22T16:20:57","end":"2019-03-22T00:00:00+00:00"}]'

        uploader.upload(TEST_IMAGE, access_control=acl_2)
        params = get_params(request_mock)

        self.assertEqual(exp_acl_2, params["access_control"])

        # Should accept a JSON string
        acl_str = '{"access_type":"anonymous","start":"2019-02-22 16:20:57 +0200","end":"2019-03-22 00:00 +0200"}'
        exp_acl_str = '[{"access_type":"anonymous","start":"2019-02-22 16:20:57 +0200","end":"2019-03-22 00:00 +0200"}]'

        uploader.upload(TEST_IMAGE, access_control=acl_str)
        params = get_params(request_mock)

        self.assertEqual(exp_acl_str, params["access_control"])

        # Should accept a list of all the above values
        list_of_acl = [acl, acl_2, acl_str]
        # Remove starting "[" and ending "]" in all expected strings and combine them into one string
        expected_list_of_acl = "[" + ",".join([v[1:-1] for v in (exp_acl, exp_acl_2, exp_acl_str)]) + "]"

        uploader.upload(TEST_IMAGE, access_control=list_of_acl)
        params = get_params(request_mock)

        self.assertEqual(expected_list_of_acl, params["access_control"])

        # Should raise ValueError on invalid values
        invalid_values = [[[]], ["not_a_dict"], [7357]]
        for invalid_value in invalid_values:
            with self.assertRaises(ValueError):
                uploader.upload(TEST_IMAGE, access_control=invalid_value)

    @patch(URLLIB3_REQUEST)
    def test_various_upload_parameters(self, request_mock):
        """Should support various parameters in upload and explicit"""
        request_mock.return_value = MOCK_RESPONSE

        options = {
            'cinemagraph_analysis': True,
            'accessibility_analysis': True,
            'media_metadata': True,
            'visual_search': True,
            'on_success': ON_SUCCESS_STR,
            'regions': {"box_1": [[1, 2], [3, 4]], "box_2": [[5, 6], [7, 8]]}
        }

        uploader.upload(TEST_IMAGE, **options)

        params = get_params(request_mock)
        for param in options.keys():
            self.assertIn(param, params)

        uploader.explicit(TEST_IMAGE, **options)

        params = get_params(request_mock)
        for param in options.keys():
            self.assertIn(param, params)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_eval_upload_parameter(self):
        """Should support eval in upload"""
        result = uploader.upload(TEST_IMAGE, eval=EVAL_STR, tags=[UNIQUE_TAG])
        self.assertEqual(str(result['context']['custom']['width']), str(TEST_IMAGE_WIDTH))
        self.assertIsInstance(result['quality_analysis'], dict)
        self.assertIsInstance(result['quality_analysis']['focus'], float)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_generate_sprite(self):
        """Should generate a sprite from all images associated with a tag or from the image urls"""
        sprite_test_tag = "sprite_test_tag{}".format(SUFFIX)
        images_quantity_in_sprite = 2

        upload_result_1 = uploader.upload(TEST_IMAGE, tags=[sprite_test_tag, UNIQUE_TAG],
                                          public_id="sprite_test_tag_1{}".format(SUFFIX))
        upload_result_2 = uploader.upload(TEST_IMAGE, tags=[sprite_test_tag, UNIQUE_TAG],
                                          public_id="sprite_test_tag_2{}".format(SUFFIX))

        result = uploader.generate_sprite(tag=sprite_test_tag, tags=[UNIQUE_TAG])
        self.assertEqual(len(result["image_infos"]), images_quantity_in_sprite)

        urls = [upload_result_1.get('url'), upload_result_2.get('url')]
        result = uploader.generate_sprite(urls=urls, tags=[UNIQUE_TAG])
        self.assertEqual(len(result["image_infos"]), images_quantity_in_sprite)

        result = uploader.generate_sprite(sprite_test_tag, transformation={"raw_transformation": "w_100"})
        self.assertIn("w_100", result["css_url"])

        result = uploader.generate_sprite(sprite_test_tag, format="jpg", width=100)
        uploader.destroy(result.get("public_id"))
        self.assertIn("f_jpg,w_100", result["css_url"])

    def test_download_sprite(self):
        """Should generate signed download url for sprite"""
        sprite_test_tag = "sprite_tag"
        url_1 = "https://res.cloudinary.com/demo/image/upload/sample"
        url_2 = "https://res.cloudinary.com/demo/image/upload/car"

        url_from_tag = uploader.download_generated_sprite(tag=sprite_test_tag)
        url_from_urls = uploader.download_generated_sprite(urls=[url_1, url_2])

        self.assertTrue(url_from_tag.startswith(
            "https://api.cloudinary.com/v1_1/" + cloudinary.config().cloud_name + "/image/sprite"))
        self.assertTrue(url_from_urls.startswith(
            "https://api.cloudinary.com/v1_1/" + cloudinary.config().cloud_name + "/image/sprite"))

        parameters = parse_qs(urlparse(url_from_tag).query)
        self.assertEqual(sprite_test_tag, parameters["tag"][0])
        self.assertEqual("download", parameters["mode"][0])
        self.assertIn("timestamp", parameters)
        self.assertIn("signature", parameters)

        parameters = parse_qs(urlparse(url_from_urls).query)
        self.assertIn(url_1, parameters["urls[]"])
        self.assertIn(url_2, parameters["urls[]"])
        self.assertEqual("download", parameters["mode"][0])
        self.assertIn("timestamp", parameters)
        self.assertIn("signature", parameters)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_multi(self):
        """Should generate a GIF, video or a PDF from all images associated with a tag or from the image urls"""
        multi_test_tag = "multi_test_tag{}".format(SUFFIX)
        upload_result_1 = uploader.upload(TEST_IMAGE, tags=[multi_test_tag, UNIQUE_TAG])
        upload_result_2 = uploader.upload(TEST_IMAGE, tags=[multi_test_tag, UNIQUE_TAG])

        # Generate multi from urls
        urls = [upload_result_1.get('url'), upload_result_2.get('url')]
        result = uploader.multi(urls=urls, crop="crop", width="0.5")
        self.assertTrue(result.get("url").endswith(".gif"))
        self.assertIn("w_0.5", result.get("url"))

        # Generate multi from tag
        result = uploader.multi(tag=multi_test_tag, transformation={"raw_transformation": "c_crop,w_0.5"})
        pdf_result = uploader.multi(tag=multi_test_tag, width=111, format="pdf")

        self.assertTrue(result.get("url").endswith(".gif"))
        self.assertIn("w_0.5", result.get("url"))
        self.assertTrue(pdf_result.get("url").endswith(".pdf"))
        self.assertIn("w_111", pdf_result.get("url"))

    def test_download_multi(self):
        """Should generate signed download url for multi"""
        multi_test_tag = "multi_test_tag"
        url_1 = "https://res.cloudinary.com/demo/image/upload/sample"
        url_2 = "https://res.cloudinary.com/demo/image/upload/car"

        url_from_tag = uploader.download_multi(tag=multi_test_tag)
        url_from_urls = uploader.download_multi(urls=[url_1, url_2])

        self.assertTrue(url_from_tag.startswith(
            "https://api.cloudinary.com/v1_1/" + cloudinary.config().cloud_name + "/image/multi"))
        self.assertTrue(url_from_urls.startswith(
            "https://api.cloudinary.com/v1_1/" + cloudinary.config().cloud_name + "/image/multi"))

        parameters = parse_qs(urlparse(url_from_tag).query)
        self.assertEqual(multi_test_tag, parameters["tag"][0])
        self.assertEqual("download", parameters["mode"][0])
        self.assertIn("timestamp", parameters)
        self.assertIn("signature", parameters)

        parameters = parse_qs(urlparse(url_from_urls).query)
        self.assertIn(url_1, parameters["urls[]"])
        self.assertIn(url_2, parameters["urls[]"])
        self.assertEqual("download", parameters["mode"][0])
        self.assertIn("timestamp", parameters)
        self.assertIn("signature", parameters)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_zip_with_target_asset_folder(self, mocker):
        """Should pass target_asset_folder parameter on archive generation"""
        mocker.return_value = MOCK_RESPONSE
        uploader.create_zip(tags="test-tag", target_asset_folder="test-asset-folder")
        self.assertEqual("test-asset-folder", get_param(mocker, "target_asset_folder"))


if __name__ == '__main__':
    unittest.main()
