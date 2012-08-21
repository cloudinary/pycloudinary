import cloudinary
from cloudinary import uploader, utils
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
  def test_text(self):
    """should successfully generate text image """
    result = uploader.text("hello world")
    self.assertGreater(result["width"], 1)
    self.assertGreater(result["height"], 1)

if __name__ == '__main__':
    unittest.main()

