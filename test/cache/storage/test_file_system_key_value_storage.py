import os
import shutil
import tempfile
import unittest

from cloudinary.cache.storage.file_system_key_value_storage import FileSystemKeyValueStorage
from test.helper_test import UNIQUE_TEST_ID, ignore_exception


class FileSystemKeyValueStorageTest(unittest.TestCase):
    key = "test_key"
    value = "test_value"

    key2 = "test_key_2"
    value2 = "test_value_2"

    def setUp(self):
        self.root_path = tempfile.mkdtemp(prefix=UNIQUE_TEST_ID)
        self.storage = FileSystemKeyValueStorage(self.root_path)

    def tearDown(self):
        with ignore_exception():
            shutil.rmtree(self.root_path, True)

    def set_test_value(self, key, value):
        """Helper method for setting value for the key"""
        with open(self.storage._get_key_full_path(key), "w") as f:
            return f.write(value)

    def get_test_value(self, key):
        """Helper method for getting value of the key"""
        with open(self.storage._get_key_full_path(key), "r") as f:
            return f.read()

    def test_init_with_non_existing_path(self):
        non_existing_root_path = self.root_path + "_"

        try:
            FileSystemKeyValueStorage(non_existing_root_path)

            self.assertTrue(os.path.exists(non_existing_root_path))
        except Exception as e:
            self.fail(str(e))
        finally:
            shutil.rmtree(non_existing_root_path, True)

    def test_set(self):
        self.storage.set(self.key, self.value)

        self.assertEqual(self.value, self.get_test_value(self.key))

        # Should set empty value
        self.storage.set(self.key, "")

        self.assertEqual("", self.get_test_value(self.key))

    def test_get(self):
        self.set_test_value(self.key, self.value)

        self.assertEqual(self.value, self.storage.get(self.key))

        self.assertIsNone(self.storage.get("non-existing-key"))

        self.set_test_value(self.key, "")

        self.assertEqual("", self.storage.get(self.key))

    def test_delete(self):
        self.storage.set(self.key, self.value)
        self.storage.set(self.key2, self.value2)

        self.assertEqual(self.value, self.storage.get(self.key))
        self.assertEqual(self.value2, self.storage.get(self.key2))

        self.assertTrue(self.storage.delete(self.key))
        self.assertIsNone(self.storage.get(self.key))

        # Should delete only one value (opposed to clear)
        self.assertEqual(self.value2, self.storage.get(self.key2))

        # Should not crash on non-existing keys
        self.assertTrue(self.storage.delete(self.key))

    def test_clear(self):
        self.storage.set(self.key, self.value)
        self.storage.set(self.key2, self.value2)

        self.assertEqual(self.value, self.storage.get(self.key))
        self.assertEqual(self.value2, self.storage.get(self.key2))

        self.assertTrue(self.storage.clear())

        self.assertIsNone(self.storage.get(self.key))
        self.assertIsNone(self.storage.get(self.key2))

        # Should clear empty cache
        self.assertTrue(self.storage.clear())
