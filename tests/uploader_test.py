import cloudinary
from cloudinary import uploader, utils, api
from cloudinary.compat import PY3, urllib2
import unittest
import tempfile
import os

TEST_IMAGE = "tests/logo.png"
TEST_IMAGE_HEIGHT = 51
TEST_IMAGE_WIDTH = 241
TEST_TAG = "pycloudinary_test"

class UploaderTest(unittest.TestCase):

    def setUp(self):
        cloudinary.reset_config()

    @classmethod
    def tearDownClass(cls):
        cloudinary.api.delete_resources_by_tag(TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload(self):
        """should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=TEST_TAG)
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_url(self):
        """should successfully upload file by url """
        result = uploader.upload("http://cloudinary.com/images/old_logo.png", tags=TEST_TAG)
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_unicode_url(self):
        """should successfully upload file by unicode url """
        result = uploader.upload(u"http://cloudinary.com/images/old_logo.png", tags=TEST_TAG)
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_data_uri(self):
        """should successfully upload file by unicode url """
        result = uploader.upload(u"data:image/png;base64,iVBORw0KGgoAA\nAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABlBMVEUAAAD///+l2Z/dAAAAM0l\nEQVR4nGP4/5/h/1+G/58ZDrAz3D/McH8yw83NDDeNGe4Ug9C9zwz3gVLMDA/A6\nP9/AFGGFyjOXZtQAAAAAElFTkSuQmCC", tags=TEST_TAG)
        self.assertEqual(result["width"], 16)
        self.assertEqual(result["height"], 16)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename(self):
        """should successfully rename a file"""
        result = uploader.upload(TEST_IMAGE, tags=TEST_TAG)
        uploader.rename(result["public_id"], result["public_id"]+"2")
        self.assertIsNotNone(api.resource(result["public_id"]+"2"))
        self.assertRaises(api.Error, uploader.rename, result["public_id"], result["public_id"]+"2")
        self.assertDictEqual(uploader.rename(result["public_id"], result["public_id"]+"2", return_error=True),
                {"error": {"http_code": 404, "message": "Resource not found - %s" % result["public_id"]}})
        result2 = uploader.upload("tests/favicon.ico", tags=TEST_TAG)
        self.assertRaises(api.Error, uploader.rename, result2["public_id"], result["public_id"]+"2")
        self.assertDictEqual(uploader.rename(result2["public_id"], result["public_id"]+"2", return_error=True),
                {"error": {"http_code": 400, "message": "to_public_id %s already exists" % (result["public_id"]+"2")}})
        uploader.rename(result2["public_id"], result["public_id"]+"2", overwrite=True)
        self.assertEqual(api.resource(result["public_id"]+"2")["format"], "ico")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_use_filename(self):
        """should successfully take use file name of uploaded file in public id if specified use_filename """
        result = uploader.upload(TEST_IMAGE, use_filename = True, tags=TEST_TAG)
        self.assertRegexpMatches(result["public_id"], 'logo_[a-z0-9]{6}')
        result = uploader.upload(TEST_IMAGE, use_filename = True, unique_filename = False, tags=TEST_TAG)
        self.assertEqual(result["public_id"], 'logo')
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_explicit(self):
        """should support explicit """
        result = uploader.explicit("cloudinary", type="twitter_name", eager=[dict(crop="scale", width="2.0")])
        url = utils.cloudinary_url("cloudinary", type="twitter_name", crop="scale", width="2.0", format="png", version=result["version"])[0]
        self.assertEqual(result["eager"][0]["url"], url)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_eager(self):
        """should support eager """
        uploader.upload(TEST_IMAGE, eager=[dict(crop="scale", width="2.0")], tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_header(self):
        """should support headers """
        uploader.upload(TEST_IMAGE, headers=["Link: 1"], tags=TEST_TAG)
        uploader.upload(TEST_IMAGE, headers={"Link": "1"}, tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_text(self):
        """should successfully generate text image """
        result = uploader.text("hello world")
        self.assertGreater(result["width"], 1)
        self.assertGreater(result["height"], 1)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_tags(self):
        """should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=TEST_TAG)
        result2 = uploader.upload(TEST_IMAGE, tags=TEST_TAG)
        uploader.add_tag("tag1", [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag2", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], [TEST_TAG, "tag1", "tag2"])
        self.assertEqual(api.resource(result2["public_id"])["tags"], [TEST_TAG, "tag1"])
        uploader.remove_tag("tag1", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], [TEST_TAG, "tag2"])
        uploader.replace_tag("tag3", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag3"])
        uploader.replace_tag(TEST_TAG, result["public_id"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats(self):
        """ should allow whitelisted formats if allowed_formats """
        result = uploader.upload(TEST_IMAGE, allowed_formats = ['png'], tags=TEST_TAG)
        self.assertEqual(result["format"], "png");

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_illegal_format(self):
        """should prevent non whitelisted formats from being uploaded if allowed_formats is specified"""
        self.assertRaises(api.Error, uploader.upload, TEST_IMAGE, allowed_formats = ['jpg'])
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_format(self):
        """should allow non whitelisted formats if type is specified and convert to that type"""
        result = uploader.upload(TEST_IMAGE, allowed_formats = ['jpg'], format= 'jpg', tags=TEST_TAG)
        self.assertEqual("jpg", result["format"])
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_face_coordinates(self):
        """should allow sending face coordinates"""
        coordinates = [[120, 30, 109, 150], [121, 31, 110, 151]]
        result = uploader.upload(TEST_IMAGE, face_coordinates = coordinates, faces = True, tags=TEST_TAG)
        self.assertEqual(coordinates, result["faces"])

        different_coordinates = [[122, 32, 111, 152]]
        custom_coordinates = [1,2,3,4]
        uploader.explicit(result["public_id"], face_coordinates = different_coordinates, custom_coordinates = custom_coordinates, faces = True, type = "upload")
        info = api.resource(result["public_id"], faces = True, coordinates = True)
        self.assertEqual(different_coordinates, info["faces"])
        self.assertEqual({"faces": different_coordinates, "custom": [custom_coordinates]}, info["coordinates"])
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_context(self):
        """should allow sending context"""
        context = {"caption": "some caption", "alt": "alternative"}
        result = uploader.upload(TEST_IMAGE, context = context, tags=TEST_TAG)
        info = api.resource(result["public_id"], context = True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_manual_moderation(self):
        """ should support setting manual moderation status """
        resource = uploader.upload(TEST_IMAGE, moderation="manual", tags=TEST_TAG)
  
        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")
        
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_raw_conversion(self):
        """ should support requesting raw_convert """ 
        with self.assertRaisesRegexp(api.Error, 'illegal is not a valid'): 
            uploader.upload("tests/docx.docx", raw_convert="illegal", resource_type="raw", tags=TEST_TAG)
  
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_categorization(self):
        """ should support requesting categorization """
        with self.assertRaisesRegexp(api.Error, 'invalid'):
            uploader.upload(TEST_IMAGE, categorization="illegal", tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_detection(self):
        """ should support requesting detection """
        with self.assertRaisesRegexp(api.Error, 'illegal is not a valid'): 
            uploader.upload(TEST_IMAGE, detection="illegal", tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_auto_tagging(self):
        """ should support requesting auto_tagging """
        with self.assertRaisesRegexp(api.Error, 'Must use'): 
            uploader.upload(TEST_IMAGE, auto_tagging=0.5, tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large(self):
        """ should support uploading large files """ 
        temp_file = tempfile.NamedTemporaryFile()
        temp_file_name = temp_file.name
        temp_file.write(b"BMJ\xB9Y\x00\x00\x00\x00\x00\x8A\x00\x00\x00|\x00\x00\x00x\x05\x00\x00x\x05\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\xC0\xB8Y\x00a\x0F\x00\x00a\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFFBGRs\x00\x00\x00\x00\x00\x00\x00\x00T\xB8\x1E\xFC\x00\x00\x00\x00\x00\x00\x00\x00fff\xFC\x00\x00\x00\x00\x00\x00\x00\x00\xC4\xF5(\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00");
        for i in range(0, 588000):
          temp_file.write(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")

        temp_file.flush()
        self.assertEqual(5880138, os.path.getsize(temp_file_name))

        resource = uploader.upload_large(temp_file_name, chunk_size = 5243000, tags = ["upload_large_tag"])
        self.assertEqual(resource["tags"], ["upload_large_tag"]);
        self.assertEqual(resource["resource_type"], "raw");

        resource = uploader.upload_large(temp_file_name, chunk_size = 5243000, tags = ["upload_large_tag"], resource_type = "image")
        self.assertEqual(resource["tags"], ["upload_large_tag"])
        self.assertEqual(resource["resource_type"], "image");
        self.assertEqual(resource["width"], 1400);
        self.assertEqual(resource["height"], 1400);

        resource = uploader.upload_large(temp_file_name, chunk_size = 5880138, tags = ["upload_large_tag"])
        self.assertEqual(resource["tags"], ["upload_large_tag"]);
        self.assertEqual(resource["resource_type"], "raw");

        temp_file.close()

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_preset(self):
        """ should support unsigned uploading using presets """
        preset = api.create_upload_preset(folder="upload_folder", unsigned=True)
        result = uploader.unsigned_upload(TEST_IMAGE, preset["name"])
        self.assertRegexpMatches(result["public_id"], '^upload_folder\/[a-z0-9]+$')
        api.delete_upload_preset(preset["name"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_background_removal(self):
        """ should support requesting background_removal """
        with self.assertRaisesRegexp(api.Error, 'is invalid'): 
            uploader.upload(TEST_IMAGE, background_removal="illegal", tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_timeout(self):
        with self.assertRaisesRegexp(cloudinary.api.Error, 'urlopen error timed out'): 
            uploader.upload(TEST_IMAGE, timeout=0.001, tags=TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret,"requires api_key/api_secret")
    def test_responsive_breakpoints(self):
        result = uploader.upload(
            TEST_IMAGE,
            responsive_breakpoints=dict(create_derived=False,
                                        transformation=dict(angle=90)))
        
        self.assertIsNotNone(result["responsive_breakpoints"])
        self.assertEqual(result["responsive_breakpoints"][0]["transformation"],
                         "a_90")
        
        result = uploader.explicit(
            result["public_id"],
            type="upload",
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
