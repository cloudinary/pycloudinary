import unittest

from cloudinary.cache import responsive_breakpoints_cache
from cloudinary.cache.adapter.key_value_cache_adapter import KeyValueCacheAdapter
from cloudinary.cache.storage.file_system_key_value_storage import FileSystemKeyValueStorage
from test.cache.storage.dummy_cache_storage import DummyCacheStorage
from test.helper_test import UNIQUE_TEST_ID


class ResponsiveBreakpointsCacheTest(unittest.TestCase):
    public_id = UNIQUE_TEST_ID
    breakpoints = [100, 200, 300, 399]

    def setUp(self):
        self.cache = responsive_breakpoints_cache.instance
        self.cache.set_cache_adapter(KeyValueCacheAdapter(DummyCacheStorage()))

    def test_rb_cache_set_get(self):
        self.cache.set(self.public_id, self.breakpoints)

        res = self.cache.get(self.public_id)

        self.assertEqual(self.breakpoints, res)

    def test_rb_cache_set_invalid_breakpoints(self):
        with self.assertRaises(ValueError):
            self.cache.set(self.public_id, "Not breakpoints at all")

    def test_rb_cache_delete(self):
        self.cache.set(self.public_id, self.breakpoints)

        self.cache.delete(self.public_id)

        res = self.cache.get(self.public_id)

        self.assertIsNone(res)

    def test_rb_cache_flush_all(self):
        self.cache.set(self.public_id, self.breakpoints)

        self.cache.flush_all()

        res = self.cache.get(self.public_id)

        self.assertIsNone(res)

    def test_rb_cache_disabled(self):
        self.cache._cache_adapter = None

        self.assertFalse(self.cache.enabled)

        self.assertFalse(self.cache.set(self.public_id, self.breakpoints))
        self.assertIsNone(self.cache.get(self.public_id))
        self.assertFalse(self.cache.delete(self.public_id))
        self.assertFalse(self.cache.flush_all())

    def test_rb_cache_filesystem_storage(self):
        self.cache.set_cache_adapter(KeyValueCacheAdapter(FileSystemKeyValueStorage(None)))

        res = None
        try:
            self.cache.set(self.public_id, self.breakpoints)
            res = self.cache.get(self.public_id)
        finally:
            self.cache.delete(self.public_id)

        self.assertEqual(self.breakpoints, res)


