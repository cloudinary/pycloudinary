import cloudinary
from cloudinary import uploader, utils, api
from cloudinary.compat import PY3
import unittest

class UploaderTest(unittest.TestCase):

    def setUp(self):
        cloudinary.reset_config()

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload(self):
        """should successfully upload file """
        result = uploader.upload("tests/logo.png")
        self.assertEqual(result["width"], 241)
        self.assertEqual(result["height"], 51)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_url(self):
        """should successfully upload file by url """
        result = uploader.upload("http://cloudinary.com/images/logo.png")
        self.assertEqual(result["width"], 241)
        self.assertEqual(result["height"], 51)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_unicode_url(self):
        """should successfully upload file by unicode url """
        result = uploader.upload(u"http://cloudinary.com/images/logo.png")
        self.assertEqual(result["width"], 241)
        self.assertEqual(result["height"], 51)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_data_uri(self):
        """should successfully upload file by unicode url """
        result = uploader.upload(u"data:image/png;base64,iVBORw0KGgoAA\nAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABlBMVEUAAAD///+l2Z/dAAAAM0l\nEQVR4nGP4/5/h/1+G/58ZDrAz3D/McH8yw83NDDeNGe4Ug9C9zwz3gVLMDA/A6\nP9/AFGGFyjOXZtQAAAAAElFTkSuQmCC")
        self.assertEqual(result["width"], 16)
        self.assertEqual(result["height"], 16)
        expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename(self):
        """should successfully rename a file"""
        result = uploader.upload("tests/logo.png")
        uploader.rename(result["public_id"], result["public_id"]+"2")
        self.assertIsNotNone(api.resource(result["public_id"]+"2"))
        result2 = uploader.upload("tests/favicon.ico")
        self.assertRaises(api.Error, uploader.rename, result2["public_id"], result["public_id"]+"2")
        uploader.rename(result2["public_id"], result["public_id"]+"2", overwrite=True)
        self.assertEqual(api.resource(result["public_id"]+"2")["format"], "ico")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_use_filename(self):
        """should successfully take use file name of uploaded file in public id if specified use_filename """
        result = uploader.upload("tests/logo.png", use_filename = True)
        self.assertRegexpMatches(result["public_id"], 'logo_[a-z0-9]{6}')
        result = uploader.upload("tests/logo.png", use_filename = True, unique_filename = False)
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
        uploader.upload("tests/logo.png", eager=[dict(crop="scale", width="2.0")])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_header(self):
        """should support headers """
        uploader.upload("tests/logo.png", headers=["Link: 1"])
        uploader.upload("tests/logo.png", headers={"Link": "1"})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_text(self):
        """should successfully generate text image """
        result = uploader.text("hello world")
        self.assertGreater(result["width"], 1)
        self.assertGreater(result["height"], 1)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_tags(self):
        """should successfully upload file """
        result = uploader.upload("tests/logo.png")
        result2 = uploader.upload("tests/logo.png")
        uploader.add_tag("tag1", [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag2", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag1", "tag2"])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1"])
        uploader.remove_tag("tag1", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag2"])
        uploader.replace_tag("tag3", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag3"])
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats(self):
        """ should allow whitelisted formats if allowed_formats """
        result = uploader.upload("tests/logo.png", allowed_formats = ['png'])
        self.assertEqual(result["format"], "png");

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_illegal_format(self):
        """should prevent non whitelisted formats from being uploaded if allowed_formats is specified"""
        self.assertRaises(api.Error, uploader.upload, "tests/logo.png", allowed_formats = ['jpg'])
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_format(self):
        """should allow non whitelisted formats if type is specified and convert to that type"""
        result = uploader.upload("tests/logo.png", allowed_formats = ['jpg'], format= 'jpg')
        self.assertEqual("jpg", result["format"])
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_face_coordinates(self):
        """should allow sending face coordinates"""
        coordinates = [[120, 30, 109, 150], [121, 31, 110, 151]]
        result = uploader.upload("tests/logo.png", face_coordinates = coordinates, faces = True)
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
        result = uploader.upload("tests/logo.png", context = context)
        info = api.resource(result["public_id"], context = True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_manual_moderation(self):
        """ should support setting manual moderation status """
        resource = uploader.upload("tests/logo.png", moderation="manual")
  
        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")
        
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_raw_conversion(self):
        """ should support requesting raw_convert """ 
        with self.assertRaisesRegexp(api.Error, 'illegal is not a valid'): 
            uploader.upload("tests/docx.docx", raw_convert="illegal", resource_type="raw")
  
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_categorization(self):
        """ should support requesting categorization """
        with self.assertRaisesRegexp(api.Error, 'illegal is not a valid'): 
            uploader.upload("tests/logo.png", categorization="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_detection(self):
        """ should support requesting detection """
        with self.assertRaisesRegexp(api.Error, 'illegal is not a valid'): 
            uploader.upload("tests/logo.png", detection="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_auto_tagging(self):
        """ should support requesting auto_tagging """
        with self.assertRaisesRegexp(api.Error, 'Must use'): 
            uploader.upload("tests/logo.png", auto_tagging=0.5)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large(self):
        """ should uploading large raw files """ 
        uploader.upload_large("tests/docx.docx")  

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_preset(self):
        """ should support unsigned uploading using presets """
        preset = api.create_upload_preset(folder="upload_folder", unsigned=True)
        result = uploader.unsigned_upload("tests/logo.png", preset["name"])
        self.assertRegexpMatches(result["public_id"], '^upload_folder\/[a-z0-9]+$')
        api.delete_upload_preset(preset["name"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_background_removal(self):
        """ should support requesting background_removal """
        with self.assertRaisesRegexp(api.Error, 'illegal is not a valid'): 
            uploader.upload("tests/logo.png", background_removal="illegal")

if __name__ == '__main__':
    unittest.main()
