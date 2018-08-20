from cloudinary.cache.storage.key_value_storage import KeyValueStorage


class DummyCacheStorage(KeyValueStorage):
    def __init__(self):
        self._dummy_cache = dict()

    def get(self, key):
        return self._dummy_cache.get(key, None)

    def set(self, key, value):
        self._dummy_cache[key] = value

        return True

    def delete(self, key):
        self._dummy_cache.pop(key, None)

        return True

    def clear(self):
        self._dummy_cache = dict()