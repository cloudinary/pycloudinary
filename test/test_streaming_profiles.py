import unittest
import cloudinary
from cloudinary import api
from urllib3 import disable_warnings

from test.helper_test import SUFFIX

disable_warnings()


class StreamingProfilesTest(unittest.TestCase):
    initialized = False
    test_id = "streaming_profiles_test_{}".format(SUFFIX)

    def setUp(self):
        if self.initialized:
            return
        self.initialized = True
        cloudinary.reset_config()
        if not cloudinary.config().api_secret:
            return

    __predefined_sp = ["4k", "full_hd", "hd", "sd", "full_hd_wifi", "full_hd_lean", "hd_lean"]

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_create_streaming_profile(self):
        """should create a streaming profile with representations"""
        name = self.test_id + "_streaming_profile"
        result = api.create_streaming_profile(
            name,
            representations=[{"transformation": {
                "bit_rate": "5m", "height": 1200, "width": 1200, "crop": "limit"
            }}])
        self.assertIn("representations", result["data"])
        reps = result["data"]["representations"]
        self.assertIsInstance(reps, list)

        # should return transformation as an array
        self.assertIsInstance(reps[0]["transformation"], list)

        tr = reps[0]["transformation"][0]
        expected = {"bit_rate": "5m", "height": 1200, "width": 1200, "crop": "limit"}
        self.assertDictEqual(expected, tr)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_list_streaming_profiles(self):
        """should list streaming profile"""
        result = api.list_streaming_profiles()
        names = [sp["name"] for sp in result["data"]]
        self.assertTrue(len(names) >= len(self.__predefined_sp))
        # streaming profiles should include the predefined profiles
        for name in self.__predefined_sp:
            self.assertIn(name, names)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_get_streaming_profile(self):
        """should get a specific streaming profile"""
        result = api.get_streaming_profile(self.__predefined_sp[0])
        self.assertIn("representations", result["data"])
        reps = result["data"]["representations"]
        self.assertIsInstance(reps, list)
        self.assertIsInstance(reps[0]["transformation"], list)

        tr = reps[0]["transformation"][0]
        self.assertIn("bit_rate", tr)
        self.assertIn("height", tr)
        self.assertIn("width", tr)
        self.assertIn("crop", tr)

    def test_update_delete_streaming_profile(self):
        name = self.test_id + "_streaming_profile_delete"
        api.create_streaming_profile(
            name,
            representations=[{"transformation": {
                "bit_rate": "5m", "height": 1200, "width": 1200, "crop": "limit"
            }}])
        result = api.update_streaming_profile(
            name,
            representations=[{"transformation": {
                "bit_rate": "5m", "height": 1000, "width": 1000, "crop": "scale"
            }}])
        self.assertIn("representations", result["data"])
        reps = result["data"]["representations"]
        self.assertIsInstance(reps, list)
        # transformation is returned as an array
        self.assertIsInstance(reps[0]["transformation"], list)

        tr = reps[0]["transformation"][0]
        expected = {"bit_rate": "5m", "height": 1000, "width": 1000, "crop": "scale"}
        self.assertDictEqual(expected, tr)

        api.delete_streaming_profile(name)
        result = api.list_streaming_profiles()
        self.assertNotIn(name, [p["name"] for p in result["data"]])
