import cloudinary
from cloudinary import CloudinaryImage
import unittest

class TestCloudinaryImage(unittest.TestCase):
  def setUp(self):
    cloudinary.config(cloud_name="test", api_secret="1234")
    self.image = CloudinaryImage("hello", format = "png")

  def test_url(self):
    """should generate url """
    self.assertEqual(self.image.url(), "http://res.cloudinary.com/test/image/upload/hello.png")

  def test_image(self):
    """should generate image """
    self.assertEqual(self.image.image(), "<img src='http://res.cloudinary.com/test/image/upload/hello.png' />")

  def test_image_unicode(self):
    """should generate image with unicode arguments """
    self.assertEqual(self.image.image(alt=u"\ua000abcd\u07b4"), u"<img src='http://res.cloudinary.com/test/image/upload/hello.png' alt='\ua000abcd\u07b4'/>")

  def test_scale(self):
    """should accept scale crop and pass width/height to image tag """
    self.assertEqual(self.image.image(crop='scale', width=100, height=100), "<img src='http://res.cloudinary.com/test/image/upload/c_scale,h_100,w_100/hello.png' height='100' width='100'/>")

  def test_validate(self):
    """should validate signature """
    self.assertFalse(self.image.validate())
    self.assertFalse(CloudinaryImage("hello", format = "png", version="1234", signature="1234").validate())
    self.assertTrue(CloudinaryImage("hello", format = "png", version="1234", signature="2aa73bf69fb50816e5509e32275b8c417dcb880d").validate())

  
if __name__ == '__main__':
    unittest.main()

