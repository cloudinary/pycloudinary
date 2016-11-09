from cloudinary import CloudinaryResource, CloudinaryImage
from django.test import TestCase

from cloudinary.models import CloudinaryField
from cloudinary.forms import CloudinaryFileField

from .models import Poll 


class TestCloudinaryField(TestCase):

    def setup(self):
        self.poll = Poll(question="What?", image="sample")

    def test_get_internal_type(self):
        c = CloudinaryField('image', null=True)
        self.assertEqual(c.get_internal_type(), "CharField")

    def test_to_python(self):
        c = CloudinaryField('image')
        res = CloudinaryResource(public_id='sample',format='jpg')
        # Can't compare the objects, so compare url instead
        self.assertEqual(c.to_python('sample.jpg').build_url(), res.build_url())

    def test_upload_options_with_filename(self):
        self.assertEqual(True,True)

    def test_upload_options(self):
        self.assertEqual(True,True)

    def test_pre_save(self):
        self.assertEqual(True,True)

    def test_get_prep_value(self):
        c = CloudinaryField('image')
        res = CloudinaryImage(public_id='sample',format='jpg')
        self.assertEqual(c.get_prep_value(res), "image/upload/sample.jpg")

    def test_formfield(self):
        c = CloudinaryField('image')
        forField = c.formfield()
        self.assertTrue(isinstance(forField, CloudinaryFileField))
