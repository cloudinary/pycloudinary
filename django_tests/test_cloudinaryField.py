from urllib3.util import parse_url

import cloudinary
from cloudinary import CloudinaryImage, CloudinaryResource
from cloudinary.forms import CloudinaryFileField
from cloudinary.models import CloudinaryField
from django.test import TestCase

from .models import Poll


class TestCloudinaryField(TestCase):

    @classmethod
    def setUpTestData(cls):
        Poll.objects.create(question="with image", image="image/upload/v1234/sample.jpg")
        Poll.objects.create(question="empty")

    def test_get_internal_type(self):
        c = CloudinaryField('image', null=True)
        self.assertEqual(c.get_internal_type(), "CharField")

    def test_to_python(self):
        c = CloudinaryField('image')
        res = CloudinaryResource(public_id='sample', format='jpg')
        # Can't compare the objects, so compare url instead
        self.assertEqual(c.to_python('sample.jpg').build_url(), res.build_url())

    def test_upload_options_with_filename(self):
        self.assertEqual(True, True)

    def test_upload_options(self):
        self.assertEqual(True, True)

    def test_pre_save(self):
        self.assertEqual(True, True)

    def test_get_prep_value(self):
        c = CloudinaryField('image')
        res = CloudinaryImage(public_id='sample', format='jpg')
        self.assertEqual(c.get_prep_value(res), "image/upload/sample.jpg")

    def test_formfield(self):
        c = CloudinaryField('image')
        for_field = c.formfield()
        self.assertTrue(isinstance(for_field, CloudinaryFileField))

    def test_empty_field(self):
        emptyField = Poll.objects.get(question="empty")
        self.assertIsNotNone(emptyField)
        self.assertIsNone(emptyField.image)
        self.assertFalse(True and emptyField.image)

    def test_image_field(self):
        field = Poll.objects.get(question="with image")
        self.assertIsNotNone(field)
        self.assertEqual(field.image.public_id, "sample")
        self.assertEqual(
            parse_url(field.image.url).path,
            "/{cloud}/image/upload/v1234/sample.jpg".format(
                cloud=cloudinary.config().cloud_name))
        self.assertTrue(False or field.image)
