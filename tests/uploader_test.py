import cloudinary
from cloudinary import uploader, utils, api
import unittest

class TestUploader(unittest.TestCase):
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
    def test_rename(self):
        """should successfully rename a file"""
        result = uploader.upload("tests/logo.png")
        uploader.rename(result["public_id"], result["public_id"]+"2")
        self.assertIsNotNone(api.resource(result["public_id"]+"2"))
        result2 = uploader.upload("tests/favicon.ico")
        self.assertRaises(Exception, uploader.rename, (result2["public_id"], result["public_id"]+"2"))
        uploader.rename(result2["public_id"], result["public_id"]+"2", overwrite=True)
        self.assertEqual(api.resource(result["public_id"]+"2")["format"], "ico")

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

if __name__ == '__main__':
    unittest.main()
