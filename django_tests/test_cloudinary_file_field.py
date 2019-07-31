from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from mock import mock

import cloudinary
from cloudinary import CloudinaryResource
from cloudinary.forms import CloudinaryFileField
from django_tests.forms import CloudinaryJsTestFileForm
from django_tests.helper_test import SUFFIX, TEST_IMAGE, TEST_IMAGE_W, TEST_IMAGE_H

API_TEST_ID = "dj_test_{}".format(SUFFIX)


class TestCloudinaryFileField(TestCase):
    def setUp(self):
        self.test_file = SimpleUploadedFile(TEST_IMAGE, b'content')

    def test_file_field(self):
        cff_no_auto_save = CloudinaryFileField(autosave=False)
        res = cff_no_auto_save.to_python(None)
        self.assertIsNone(res)
        # without auto_save File is untouched
        res = cff_no_auto_save.to_python(self.test_file)
        self.assertIsInstance(res, SimpleUploadedFile)

        # when auto_save is used, resource is uploaded to Cloudinary and CloudinaryResource is returned
        cff_auto_save = CloudinaryFileField(autosave=True, options={"public_id": API_TEST_ID})
        mocked_resource = cloudinary.CloudinaryResource(metadata={"width": TEST_IMAGE_W, "height": TEST_IMAGE_H},
                                                        type="upload", public_id=API_TEST_ID, resource_type="image")

        with mock.patch('cloudinary.uploader.upload_image', return_value=mocked_resource) as upload_mock:
            res = cff_auto_save.to_python(self.test_file)

        self.assertTrue(upload_mock.called)
        self.assertIsInstance(res, CloudinaryResource)
        self.assertEqual(API_TEST_ID, res.public_id)

    def test_js_file_field(self):
        js_file_form = CloudinaryJsTestFileForm()

        rendered_form = js_file_form.as_p()

        self.assertIn("margin-top: 30px", rendered_form)
        self.assertIn("directly_uploaded", rendered_form)
        self.assertIn("c_fill,h_100,w_150", rendered_form)
        self.assertIn("c_limit,h_1000,w_1000", rendered_form)

    def tearDown(self):
        pass
