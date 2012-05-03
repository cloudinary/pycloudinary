import pycloudinary
from pycloudinary import uploader, utils
import unittest

class TestUploader(unittest.TestCase):
  def setUp(self):
    pycloudinary.reset_config()
  
  def test_upload(self):
    """should successfully upload file """
    if not pycloudinary.config().api_secret: 
      print "Please setup environment for upload test to run"
      return
    result = uploader.upload("tests/logo.png")
    self.assertEqual(result["width"], 241)
    self.assertEqual(result["height"], 51)
    expected_signature = utils.api_sign_request(dict(public_id=result["public_id"], version=result["version"]), pycloudinary.config().api_secret)
    self.assertEqual(result["signature"], expected_signature)

if __name__ == '__main__':
    unittest.main()

