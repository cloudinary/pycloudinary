import re

import cloudinary
from cloudinary import CloudinaryImage
import unittest
import six


class ImageTest(unittest.TestCase):
    def setUp(self):
        cloudinary.reset_config()
        cloudinary.config(cloud_name="test", api_secret="1234")
        self.image = CloudinaryImage("hello", format="png")

    def test_build_url(self):
        """should generate url """
        self.assertEqual(self.image.build_url(), 'http://res.cloudinary.com/test/image/upload/hello.png')

    def test_url(self):
        """should url property """
        self.assertEqual(self.image.url, 'http://res.cloudinary.com/test/image/upload/hello.png')

    def test_image(self):
        """should generate image """
        self.assertEqual(self.image.image(), '<img src="http://res.cloudinary.com/test/image/upload/hello.png"/>')

    def test_image_unicode(self):
        """should generate image with unicode arguments """
        self.assertEqual(
            self.image.image(alt=u"\ua000abcd\u07b4"),
            u'<img alt="\ua000abcd\u07b4" src="http://res.cloudinary.com/test/image/upload/hello.png"/>')

    def test_scale(self):
        """should accept scale crop and pass width/height to image tag """
        self.assertEqual(
            self.image.image(crop="scale", width=100, height=100),
            '<img height="100" src="http://res.cloudinary.com/test/image/upload/c_scale,h_100,w_100/hello.png" width="100"/>')

    def test_validate(self):
        """should validate signature """
        self.assertFalse(self.image.validate())
        self.assertFalse(CloudinaryImage("hello", format="png", version="1234", signature="1234").validate())
        self.assertTrue(CloudinaryImage("hello", format="png", version="1234",
                                        signature="2aa73bf69fb50816e5509e32275b8c417dcb880d").validate())

    def test_responsive_width(self):
        """should add responsive width transformation"""
        self.assertEqual(self.image.image(responsive_width=True),
                         '<img class="cld-responsive" data-src="http://res.cloudinary.com/test/image/upload/c_limit,w_auto/hello.png"/>')

    def test_width_auto(self):
        """should support width=auto """
        self.assertEqual(self.image.image(width="auto", crop="limit"),
                         '<img class="cld-responsive" data-src="http://res.cloudinary.com/test/image/upload/c_limit,w_auto/hello.png"/>')

    def test_dpr_auto(self):
        """should support dpr=auto """
        self.assertEqual(self.image.image(dpr="auto"),
                         '<img class="cld-hidpi" data-src="http://res.cloudinary.com/test/image/upload/dpr_auto/hello.png"/>')

    def test_effect_art_incognito(self):
        """should support effect art:incognito """
        self.assertEqual(self.image.image(effect="art:incognito"),
                         '<img src="http://res.cloudinary.com/test/image/upload/e_art:incognito/hello.png"/>')

    def shared_client_hints(self, **options):
        """should not use data-src or set responsive class"""
        tag = CloudinaryImage('sample.jpg').image(**options)
        six.assertRegex(self, tag, '<img.*>', "should not use data-src or set responsive class")
        self.assertIsNone(re.match('<.* class.*>', tag), 
                          "should not use data-src or set responsive class")
        self.assertIsNone(re.match('\bdata-src\b', tag), 
                          "should not use data-src or set responsive class")
        six.assertRegex(self, tag,
                        'src=["\']http://res.cloudinary.com/test/image/upload/c_scale,dpr_auto,w_auto/sample.jpg["\']',
                        "should not use data-src or set responsive class")
        cloudinary.config(responsive=True)
        tag = CloudinaryImage('sample.jpg').image(**options)
        six.assertRegex(self, tag, '<img.*>')
        self.assertIsNone(re.match('<.* class.*>', tag), "should override responsive")
        self.assertIsNone(re.match('\bdata-src\b', tag), "should override responsive")
        six.assertRegex(self, tag,
                        'src=["\']http://res.cloudinary.com/test/image/upload/c_scale,dpr_auto,w_auto/sample.jpg["\']',
                        "should override responsive")

    def test_client_hints_as_options(self):
        self.shared_client_hints(dpr="auto", cloud_name="test", width="auto", crop="scale", client_hints=True)

    def test_client_hints_as_global(self):
        cloudinary.config(client_hints=True)
        self.shared_client_hints(dpr="auto", cloud_name="test", width="auto", crop="scale")

    def test_client_hints_as_false(self):
        """should use normal responsive behaviour"""
        cloudinary.config(responsive=True)
        tag = CloudinaryImage('sample.jpg').image(width="auto", crop="scale", cloud_name="test", client_hints=False)
        six.assertRegex(self, tag, '<img.*>')
        six.assertRegex(self, tag, 'class=["\']cld-responsive["\']')
        six.assertRegex(self, tag,
                        'data-src=["\']http://res.cloudinary.com/test/image/upload/c_scale,w_auto/sample.jpg["\']')

    def test_width_auto_breakpoints(self):
        """supports auto width"""
        tag = CloudinaryImage('sample.jpg')\
            .image(crop="scale", dpr="auto", cloud_name="test", width="auto:breakpoints", client_hints=True)
        six.assertRegex(self, tag,
                        'src=["\']http://res.cloudinary.com/test/image/upload/c_scale,dpr_auto,w_auto:breakpoints/sample.jpg["\']')

if __name__ == "__main__":
    unittest.main()
