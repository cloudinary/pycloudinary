import os
import tempfile
import unittest

from mock import patch
import cloudinary
import six
from cloudinary import uploader, utils, api

from urllib3 import disable_warnings, HTTPResponse
from urllib3.util import parse_url
from tests.test_helper import *

if six.PY2:
    MOCK_RESPONSE = HTTPResponse(body='{"foo":"bar"}')
else:
    MOCK_RESPONSE = HTTPResponse(body='{"foo":"bar"}'.encode("UTF-8"))

disable_warnings()

TEST_IMAGE_HEIGHT = 51
TEST_IMAGE_WIDTH = 241
UNIQUE_TAG = "up_test_uploader_{}".format(SUFFIX)
TEST_DOCX_ID = "test_docx_{}".format(SUFFIX)


class UploaderTest(unittest.TestCase):

    def setUp(self):
        cloudinary.reset_config()

    @classmethod
    def tearDownClass(cls):
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG)
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG, resource_type='raw')
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG, type='twitter_name')
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG, type='text')
        cloudinary.api.delete_resources([TEST_IMAGE])
        cloudinary.api.delete_resources([TEST_DOCX_ID], resource_type='raw')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload(self):
        """should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]),
                                                    cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_async(self, mocker):
        """should pass async value """
        mocker.return_value = MOCK_RESPONSE
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], async=True)
        params = mocker.call_args[0][2]
        self.assertTrue(params['async'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_ocr(self, mocker):
        """should pass ocr value """
        mocker.return_value = MOCK_RESPONSE
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], ocr='adv_ocr')
        args, kargs = mocker.call_args
        self.assertEqual(get_params(args)['ocr'], 'adv_ocr')

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_quality_override(self, mocker):
        """should pass quality_override """
        mocker.return_value = MOCK_RESPONSE
        test_values = ['auto:advanced', 'auto:best', '80:420', 'none']
        for quality in test_values:
            uploader.upload(TEST_IMAGE, tags=TEST_TAG, quality_override=quality)
            params = mocker.call_args[0][2]
            self.assertEqual(params['quality_override'], quality)
        # verify explicit works too
        uploader.explicit(TEST_IMAGE, quality_override='auto:best')
        params = mocker.call_args[0][2]
        self.assertEqual(params['quality_override'], 'auto:best')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_url(self):
        """should successfully upload file by url """
        result = uploader.upload("http://cloudinary.com/images/old_logo.png", tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]),
                                                    cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_unicode_url(self):
        """should successfully upload file by unicode url """
        result = uploader.upload(u"http://cloudinary.com/images/old_logo.png", tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]),
                                                    cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_data_uri(self):
        """should successfully upload file by data url """
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
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]),
                                                    cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename(self):
        """should successfully rename a file"""
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        uploader.rename(result["public_id"], result["public_id"]+"2")
        self.assertIsNotNone(api.resource(result["public_id"]+"2"))
        result2 = uploader.upload("tests/favicon.ico", tags=[UNIQUE_TAG])
        self.assertRaises(api.Error, uploader.rename, result2["public_id"], result["public_id"]+"2")
        uploader.rename(result2["public_id"], result["public_id"]+"2", overwrite=True)
        self.assertEqual(api.resource(result["public_id"]+"2")["format"], "ico")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_use_filename(self):
        """should successfully take use file name of uploaded file in public id if specified use_filename """
        result = uploader.upload(TEST_IMAGE, use_filename=True, tags=[UNIQUE_TAG])
        six.assertRegex(self, result["public_id"], 'logo_[a-z0-9]{6}')
        result = uploader.upload(TEST_IMAGE, use_filename=True, unique_filename=False, tags=[UNIQUE_TAG])
        self.assertEqual(result["public_id"], 'logo')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_explicit(self):
        """should support explicit """
        result = uploader.explicit("cloudinary", type="twitter_name",
                                   eager=[dict(crop="scale", width="2.0")], tags=[UNIQUE_TAG])
        url = utils.cloudinary_url("cloudinary", type="twitter_name", crop="scale", width="2.0", format="png",
                                   version=result["version"])[0]
        actual = result["eager"][0]["url"]
        self.assertEqual(parse_url(actual).path, parse_url(url).path)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_eager(self):
        """should support eager """
        uploader.upload(TEST_IMAGE, eager=[dict(crop="scale", width="2.0")], tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_header(self):
        """should support headers """
        uploader.upload(TEST_IMAGE, headers=["Link: 1"], tags=[UNIQUE_TAG])
        uploader.upload(TEST_IMAGE, headers={"Link": "1"}, tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_text(self):
        """should successfully generate text image """
        result = uploader.text("hello world", tags=[UNIQUE_TAG])
        self.assertGreater(result["width"], 1)
        self.assertGreater(result["height"], 1)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_tags(self):
        """should successfully upload file """
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
    def test_allowed_formats(self):
        """ should allow whitelisted formats if allowed_formats """
        result = uploader.upload(TEST_IMAGE, allowed_formats=['png'], tags=[UNIQUE_TAG])
        self.assertEqual(result["format"], "png")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_illegal_format(self):
        """should prevent non whitelisted formats from being uploaded if allowed_formats is specified"""
        self.assertRaises(api.Error, uploader.upload, TEST_IMAGE, allowed_formats=['jpg'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_format(self):
        """should allow non whitelisted formats if type is specified and convert to that type"""
        result = uploader.upload(TEST_IMAGE, allowed_formats=['jpg'], format='jpg', tags=[UNIQUE_TAG])
        self.assertEqual("jpg", result["format"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_face_coordinates(self):
        """should allow sending face coordinates"""
        coordinates = [[120, 30, 109, 150], [121, 31, 110, 151]]
        result_coordinates = [[120, 30, 109, 51], [121, 31, 110, 51]]
        result = uploader.upload(TEST_IMAGE, face_coordinates=coordinates, faces=True, tags=[UNIQUE_TAG])
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
        """should allow sending context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, context=context, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_manual_moderation(self):
        """ should support setting manual moderation status """
        resource = uploader.upload(TEST_IMAGE, moderation="manual", tags=[UNIQUE_TAG])

        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_raw_conversion(self):
        """ should support requesting raw_convert """
        with six.assertRaisesRegex(self, api.Error, 'illegal is not a valid'):
            uploader.upload("tests/docx.docx", public_id=TEST_DOCX_ID, raw_convert="illegal",
                            resource_type="raw", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_categorization(self):
        """ should support requesting categorization """
        with six.assertRaisesRegex(self, api.Error, 'invalid'):
            uploader.upload(TEST_IMAGE, categorization="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_detection(self):
        """ should support requesting detection """
        with six.assertRaisesRegex(self, api.Error, 'illegal is not a valid'): 
            uploader.upload(TEST_IMAGE, detection="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large(self):
        """ should support uploading large files """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file_name = temp_file.name
        temp_file.write(b"BMJ\xB9Y\x00\x00\x00\x00\x00\x8A\x00\x00\x00|\x00\x00\x00x\x05\x00\x00x\x05\x00\x00\x01\
\x00\x18\x00\x00\x00\x00\x00\xC0\xB8Y\x00a\x0F\x00\x00a\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\
\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFFBGRs\x00\x00\x00\x00\x00\x00\x00\x00T\xB8\x1E\xFC\x00\x00\x00\x00\
\x00\x00\x00\x00fff\xFC\x00\x00\x00\x00\x00\x00\x00\x00\xC4\xF5(\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        for i in range(0, 588000):
            temp_file.write(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")

        temp_file.flush()
        self.assertEqual(5880138, os.path.getsize(temp_file_name))

        resource = uploader.upload_large(temp_file_name, chunk_size=5243000, tags=["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource["tags"], ["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource["resource_type"], "raw")

        resource2 = uploader.upload_large(temp_file_name, chunk_size=5243000, tags=["upload_large_tag", UNIQUE_TAG],
                                         resource_type="image")
        self.assertEqual(resource2["tags"], ["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource2["resource_type"], "image")
        self.assertEqual(resource2["width"], 1400)
        self.assertEqual(resource2["height"], 1400)

        resource3 = uploader.upload_large(temp_file_name, chunk_size=5880138, tags=["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource3["tags"], ["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource3["resource_type"], "raw")

        temp_file.close()

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_preset(self):
        """ should support unsigned uploading using presets """
        preset = api.create_upload_preset(folder="upload_folder", unsigned=True, tags=[UNIQUE_TAG])
        result = uploader.unsigned_upload(TEST_IMAGE, preset["name"], tags=[UNIQUE_TAG])
        six.assertRegex(self, result["public_id"], '^upload_folder\/[a-z0-9]+$')
        api.delete_upload_preset(preset["name"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_background_removal(self):
        """ should support requesting background_removal """
        with six.assertRaisesRegex(self, api.Error, 'is invalid'):
            uploader.upload(TEST_IMAGE, background_removal="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_timeout(self):
        with six.assertRaisesRegex(self, cloudinary.api.Error, 'timed out'):
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

if __name__ == '__main__':
    unittest.main()
