import cloudinary
from cloudinary import uploader, utils, api
from cloudinary.compat import PY3, urllib2
import unittest
import tempfile
import os
import zipfile

TEST_TAG = "pycloudinary_test"

class ArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        uploader.upload("tests/logo.png", tags = [TEST_TAG])
        uploader.upload("tests/logo.png", tags = [TEST_TAG], transformation=dict(width=10))
    
    @classmethod
    def tearDownClass(cls):
        api.delete_resources_by_tag(TEST_TAG)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_archive(self):
        """should successfully generate an archive"""
        result = uploader.create_archive(tags = [TEST_TAG])
        self.assertEqual(2, result.get("file_count"))
        result = uploader.create_zip(tags = [TEST_TAG], transformations = [{"width": 0.5},{"width": 2.0}])
        self.assertEqual(4, result.get("file_count"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_archive_url(self):
        result = utils.download_zip_url(tags = [TEST_TAG], transformations = [{"width": 0.5},{"width": 2.0}])
        response = urllib2.urlopen(result)
        temp_file = tempfile.NamedTemporaryFile()
        temp_file_name = temp_file.name
        temp_file.write(response.read())
        temp_file.flush()
        with zipfile.ZipFile(temp_file_name, 'r') as zip_file:
            infos = zip_file.infolist()
            self.assertEqual(4, len(infos))
        temp_file.close()
        

if __name__ == '__main__':
    unittest.main()
