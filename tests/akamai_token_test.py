import re
import time
import unittest
import cloudinary
from cloudinary import akamai_token 


class AkamaiTokenTest(unittest.TestCase):
    def setUp(self):
        cloudinary.config(akamai_key='00112233FF99')

    def tearDown(self):
        cloudinary.reset_config()

    def test_generate_with_start_time_and_window(self):
        token = akamai_token.generate('/image/*', 1111111111, 300)
        self.assertEqual(token,
                         '__cld_token__=st=1111111111~exp=1111111411~acl=/image/*~hmac'
                         '=0854e8b6b6a46471a80b2dc28c69bd352d977a67d031755cc6f3486c121b43af',
                         'it should generate an Akamai token with start_time and window')

    def test_generate_with_window(self):
        first_exp = int(time.mktime(time.gmtime())) + 300
        time.sleep(1)
        token = akamai_token.generate('*', window=300)
        time.sleep(1)
        second_exp = int(time.mktime(time.gmtime())) + 300

        match = re.search(r"exp=(\d+)", token)
        self.assertIsNotNone(match)
        expiration = int(match.group(1))
        self.assertGreaterEqual(expiration, first_exp)
        self.assertLessEqual(expiration, second_exp)
        self.assertEqual(token, akamai_token.generate("*", end_time=expiration))

    def test_key_override(self):
        self.assertEqual(akamai_token.generate("*", end_time=10000000, key="00aabbff"),
                         "__cld_token__=exp=10000000~acl=*~hmac"
                         "=030eafb6b19e499659d699b3d43e7595e35e3c0060e8a71904b3b8c8759f4890")

    def test_throws(self):
        self.assertRaises(Exception, akamai_token.generate, acl="*")

if __name__ == '__main__':
    unittest.main()
