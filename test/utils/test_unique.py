import unittest

from cloudinary.utils import unique


class UniqueTest(unittest.TestCase):
    def test_when_collection_is_array_with_no_key_function(self):
        self.assertEqual(
            unique(["image", "picture", "banana", "image", "picture"]),
            ["image", "picture", "banana"]
        )

    def test_when_collection_is_array_with_key_function(self):
        self.assertEqual(
            unique(["image", "word1", "picture", "banana", "image", "picture"], key=len),
            ["image", "picture", "banana"]
        )

    def test_handles_hashes_with_correct_key_function(self):
        self.assertEqual(
            unique(
                [{"image": "up"}, {"picture": 1}, {"banana": "left"}, {"image": "down"}, {"picture": 0}],
                key=lambda x: next(iter(x))),
            [{"image": "down"}, {"picture": 0}, {"banana": "left"}]
        )


if __name__ == '__main__':
    unittest.main()
