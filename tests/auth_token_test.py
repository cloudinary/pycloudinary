import os
import unittest

import cloudinary

KEY = '00112233FF99'
ALT_KEY = "CCBB2233FF00"


class AuthTokenTest(unittest.TestCase):
    def setUp(self):
        self.url_backup = os.environ.get("CLOUDINARY_URL")
        os.environ["CLOUDINARY_URL"] = "cloudinary://a:b@test123"
        cloudinary.reset_config()
        cloudinary.config(auth_token={"key":KEY, "duration": 300, "start_time": 11111111})

    def tearDown(self):
        os.environ["CLOUDINARY_URL"] = self.url_backup
        cloudinary.reset_config()

    def test_generate_with_start_time_and_duration(self):
        token = cloudinary.utils.generate_auth_token(acl='/image/*', start_time=1111111111, duration=300)
        self.assertEqual('__cld_token__=st=1111111111~exp=1111111411~acl=%2fimage%2f%2a~hmac'
                         '=0d5b0c9c1485ee162c459879fe62e06caa23bc26fec92d58bd100f2e1592eac6', token) 

    
    def test_should_add_token_if_authToken_is_globally_set_and_signed_is_True(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url( "sample.jpg", sign_url=True, resource_type="image", type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/v1486020273/sample.jpg"
                              "?__cld_token__=st=11111111~exp=11111411~hmac"
                              "=8db0d753ee7bbb9e2eaf8698ca3797436ba4c20e31f44527e43b6a6e995cfdb3") 

    def test_should_add_token_for_public_resource(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url( "sample.jpg", sign_url=True, resource_type="image", type="public", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/public/v1486020273/sample.jpg?__cld_token__=st"
                              "=11111111~exp=11111411~hmac=c2b77d9f81be6d89b5d0ebc67b671557e88a40bcf03dd4a6997ff4b994ceb80e") 

    def test_should_not_add_token_if_signed_is_false(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url( "sample.jpg", type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/v1486020273/sample.jpg")

    def test_null_token(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url( "sample.jpg", auth_token=False, sign_url=True, type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/s--v2fTPYTu--/v1486020273/sample.jpg")

    def test_explicit_authToken_should_override_global_setting(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url( "sample.jpg", sign_url=True, auth_token={ "key": ALT_KEY, "start_time": 222222222, "duration": 100 }, type="authenticated", transformation={ "crop": "scale", "width": 300 })
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/c_scale,"
                              "w_300/sample.jpg?__cld_token__=st=222222222~exp=222222322~hmac"
                              "=7d276841d70c4ecbd0708275cd6a82e1f08e47838fbb0bceb2538e06ddfa3029") 

    def test_should_compute_expiration_as_start_time_plus_duration(self):
        cloudinary.config(private_cdn=True)
        token = { "key": KEY, "start_time": 11111111, "duration": 300 }
        url, _   = cloudinary.utils.cloudinary_url( "sample.jpg", sign_url=True, auth_token=token, resource_type="image", type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/v1486020273/sample.jpg"
                              "?__cld_token__=st=11111111~exp=11111411~hmac"
                              "=8db0d753ee7bbb9e2eaf8698ca3797436ba4c20e31f44527e43b6a6e995cfdb3") 

    def test_generate_token_string(self):
        user                      = "foobar" # we can't rely on the default "now" value in tests
        tokenOptions              = { "key": KEY, "duration": 300, "acl": "/*/t_%s" % user }
        tokenOptions["start_time"] = 222222222 # we can't rely on the default "now" value in tests
        cookieToken               = cloudinary.utils.generate_auth_token( **tokenOptions)
        self.assertEqual(cookieToken, "__cld_token__=st=222222222~exp=222222522~acl=%2f%2a%2ft_foobar~hmac=1284376353c1c43d6f6a98f2813c5596f4ff6f34d837cd853fd8c3c9e7f8428c")

    def test_must_provide_expiration_or_duration(self):
        self.assertRaises(Exception, cloudinary.utils.generate_auth_token, acl="*", expiration=None, duration=None)

if __name__ == '__main__':
    unittest.main()
