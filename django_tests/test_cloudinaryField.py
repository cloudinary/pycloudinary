import os
import unittest

from mock import mock
from urllib3.util import parse_url

import cloudinary
from cloudinary import CloudinaryImage, CloudinaryResource, uploader
from cloudinary.forms import CloudinaryFileField
from cloudinary.models import CloudinaryField
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Poll
from django_tests.helper_test import SUFFIX, TEST_IMAGE, TEST_IMAGE_W, TEST_IMAGE_H, UNIQUE_TEST_ID

API_TEST_ID = "dj_test_{}".format(SUFFIX)


class TestCloudinaryField(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poll.objects.create(question="with image", image="image/upload/v1234/{}.jpg".format(API_TEST_ID))
        Poll.objects.create(question="empty")

    def setUp(self):
        self.p = Poll()
        self.p.image = SimpleUploadedFile(TEST_IMAGE, b'')

    def test_get_internal_type(self):
        c = CloudinaryField('image', null=True)
        self.assertEqual(c.get_internal_type(), "CharField")

    def test_to_python(self):
        c = CloudinaryField('image')
        res = CloudinaryResource(public_id=API_TEST_ID, format='jpg')
        # Can't compare the objects, so compare url instead
        self.assertEqual(c.to_python('{}.jpg'.format(API_TEST_ID)).build_url(), res.build_url())

    def test_upload_options_with_filename(self):
        c = CloudinaryField('image', filename=UNIQUE_TEST_ID)
        c.set_attributes_from_name('image')
        mocked_resource = cloudinary.CloudinaryResource(type="upload", public_id=TEST_IMAGE, resource_type="image")

        with mock.patch('cloudinary.uploader.upload_resource', return_value=mocked_resource) as upload_mock:
            c.pre_save(self.p, None)

        self.assertTrue(upload_mock.called)
        self.assertEqual(upload_mock.call_args[1]['filename'], UNIQUE_TEST_ID)

    def test_upload_options(self):
        c = CloudinaryField('image', width_field="image_width", height_field="image_height", unique_filename='true',
                            use_filename='true', phash='true')
        c.set_attributes_from_name('image')
        mocked_resource = cloudinary.CloudinaryResource(metadata={"width": TEST_IMAGE_W, "height": TEST_IMAGE_H},
                                                        type="upload", public_id=TEST_IMAGE, resource_type="image")

        with mock.patch('cloudinary.uploader.upload_resource', return_value=mocked_resource) as upload_mock:
            c.pre_save(self.p, None)

        self.assertTrue(upload_mock.called)
        self.assertEqual(upload_mock.call_args[1]['unique_filename'], 'true')
        self.assertEqual(upload_mock.call_args[1]['use_filename'], 'true')
        self.assertEqual(upload_mock.call_args[1]['phash'], 'true')

    def test_pre_save(self):
        c = CloudinaryField('image', width_field="image_width", height_field="image_height")
        c.set_attributes_from_name('image')
        mocked_resource = cloudinary.CloudinaryResource(metadata={"width": TEST_IMAGE_W, "height": TEST_IMAGE_H},
                                                        type="upload", public_id=TEST_IMAGE, resource_type="image")

        with mock.patch('cloudinary.uploader.upload_resource', return_value=mocked_resource) as upload_mock:
            prep_value = c.pre_save(self.p, None)

        self.assertTrue(upload_mock.called)
        self.assertEqual(".png", os.path.splitext(prep_value)[1])
        self.assertEqual(TEST_IMAGE_W, self.p.image_width)
        self.assertEqual(TEST_IMAGE_H, self.p.image_height)


        # check empty values handling
        self.p.image = SimpleUploadedFile(TEST_IMAGE, b'')
        mocked_resource_empty = cloudinary.CloudinaryResource(metadata={})
        with mock.patch('cloudinary.uploader.upload_resource', return_value=mocked_resource_empty) as upload_mock:
            c.pre_save(self.p, None)

        self.assertTrue(upload_mock.called)
        self.assertIsNone(self.p.image_width)
        self.assertIsNone(self.p.image_height)

    def test_get_prep_value(self):
        c = CloudinaryField('image')
        res = CloudinaryImage(public_id=API_TEST_ID, format='jpg')
        self.assertEqual(c.get_prep_value(res), "image/upload/{}.jpg".format(API_TEST_ID))

    def test_value_to_string(self):
        c = CloudinaryField('image')
        c.set_attributes_from_name('image')
        image_field = Poll.objects.get(question="with image")
        value_string = c.value_to_string(image_field)
        self.assertEqual("image/upload/v1234/{name}.jpg".format(name=API_TEST_ID), value_string)

    def test_formfield(self):
        c = CloudinaryField('image')
        form_field = c.formfield()
        self.assertTrue(isinstance(form_field, CloudinaryFileField))

    def test_empty_field(self):
        emptyField = Poll.objects.get(question="empty")
        self.assertIsNotNone(emptyField)
        self.assertIsNone(emptyField.image)
        self.assertFalse(True and emptyField.image)

    def test_image_field(self):
        field = Poll.objects.get(question="with image")
        self.assertIsNotNone(field)
        self.assertEqual(field.image.public_id, API_TEST_ID)
        self.assertEqual(
            parse_url(field.image.url).path,
            "/{cloud}/image/upload/v1234/{name}.jpg".format(cloud=cloudinary.config().cloud_name, name=API_TEST_ID)
        )
        self.assertTrue(False or field.image)
