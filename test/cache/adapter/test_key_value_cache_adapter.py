import unittest

from cloudinary.cache.adapter.key_value_cache_adapter import KeyValueCacheAdapter
from test.cache.storage.dummy_cache_storage import DummyCacheStorage


class KeyValueCacheAdapterTest(unittest.TestCase):
    parameters = {"public_id": "public_id",
                  "type": "upload",
                  "resource_type": "image",
                  "transformation": "w_100",
                  "format": "jpg"}
    value = [100, 200, 300, 399]
    parameters2 = {"public_id": "public_id2",
                   "type": "fetch",
                   "resource_type": "image",
                   "transformation": "w_300",
                   "format": "png"}
    value2 = [101, 201, 301, 398]

    def setUp(self):
        self.storage = DummyCacheStorage()
        self.adapter = KeyValueCacheAdapter(self.storage)

    def test_initialization(self):
        """Should be successfully initialized with a valid storage"""
        valid_storage = DummyCacheStorage()
        valid_adapter = KeyValueCacheAdapter(valid_storage)

        self.assertEqual(valid_storage, valid_adapter._key_value_storage)

    def test_invalid_initialization(self):
        invalid_storage_providers = [
            None,
            'notAStorage',
            '',
            5375,
            [],
            True,
            object
        ]

        for invalid_storage_provider in invalid_storage_providers:
            with self.assertRaises(ValueError):
                KeyValueCacheAdapter(invalid_storage_provider)

    def test_generate_cache_key(self):
        values = [
            ("467d06e5a695b15468f9362e5a58d44de523026b",
             self.parameters),
            ("1576396c59fc50ac8dc37b75e1184268882c9bc2",
             dict(self.parameters, transformation="", format=None)),
            ("d8d824ca4e9ac735544ff3c45c1df67749cc1520",
             dict(self.parameters, type="", resource_type=None))
        ]

        for value in values:
            self.assertEqual(value[0], self.adapter.generate_cache_key(**value[1]))

    def test_get_set(self):
        self.adapter.set(value=self.value, **self.parameters)
        actual_value = self.adapter.get(**self.parameters)

        self.assertEqual(self.value, actual_value)

    def test_delete(self):
        self.adapter.set(value=self.value, **self.parameters)
        actual_value = self.adapter.get(**self.parameters)

        self.assertEqual(self.value, actual_value)

        self.adapter.delete(**self.parameters)
        deleted_value = self.adapter.get(**self.parameters)

        self.assertIsNone(deleted_value)

        # Delete non-existing key
        result = self.adapter.delete(**self.parameters)

        self.assertTrue(result)

    def test_flush_all(self):

        self.adapter.set(value=self.value, **self.parameters)
        self.adapter.set(value=self.value2, **self.parameters2)

        actual_value = self.adapter.get(**self.parameters)
        actual_value2 = self.adapter.get(**self.parameters2)

        self.assertEqual(self.value, actual_value)
        self.assertEqual(self.value2, actual_value2)

        self.adapter.flush_all()

        deleted_value = self.adapter.get(**self.parameters)
        deleted_value2 = self.adapter.get(**self.parameters2)

        self.assertIsNone(deleted_value)
        self.assertIsNone(deleted_value2)
