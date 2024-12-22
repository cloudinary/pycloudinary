import os
import unittest

import cloudinary
from test.helper_test import ignore_exception

KEY = '00112233FF99'
ALT_KEY = "CCBB2233FF00"


class AuthTokenTest(unittest.TestCase):
    def setUp(self):
        self.url_backup = os.environ.get("CLOUDINARY_URL")
        os.environ["CLOUDINARY_URL"] = ("cloudinary://a:b@test123?"
                                        "auth_token[duration]=300"
                                        "&auth_token[start_time]=11111111"
                                        "&auth_token[key]=" + KEY)
        cloudinary.reset_config()

    def tearDown(self):
        with ignore_exception():
            os.environ["CLOUDINARY_URL"] = self.url_backup
            cloudinary.reset_config()

    def test_generate_with_start_time_and_duration(self):
        token = cloudinary.utils.generate_auth_token(acl='/image/*', start_time=1111111111, duration=300)
        self.assertEqual('__cld_token__=st=1111111111~exp=1111111411~acl=%2fimage%2f*~hmac'
                         '=1751370bcc6cfe9e03f30dd1a9722ba0f2cdca283fa3e6df3342a00a7528cc51', token)

    def test_should_add_token_if_authToken_is_globally_set_and_signed_is_True(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", sign_url=True, resource_type="image",
                                                 type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/v1486020273/sample.jpg"
                              "?__cld_token__=st=11111111~exp=11111411~hmac"
                              "=8db0d753ee7bbb9e2eaf8698ca3797436ba4c20e31f44527e43b6a6e995cfdb3")

    def test_should_add_token_for_public_resource(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", sign_url=True, resource_type="image", type="public",
                                                 version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/public/v1486020273/sample.jpg?__cld_token__=st"
                              "=11111111~exp=11111411~hmac="
                              "c2b77d9f81be6d89b5d0ebc67b671557e88a40bcf03dd4a6997ff4b994ceb80e")

    def test_should_not_add_token_if_signed_is_false(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/v1486020273/sample.jpg")

    def test_null_token(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", auth_token=False, sign_url=True, type="authenticated",
                                                 version="1486020273")
        self.assertEqual(
            url,
            "http://test123-res.cloudinary.com/image/authenticated/s--v2fTPYTu--/v1486020273/sample.jpg"
        )

    def test_explicit_authToken_should_override_global_setting(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", sign_url=True,
                                                 auth_token={"key": ALT_KEY, "start_time": 222222222, "duration": 100},
                                                 type="authenticated", transformation={"crop": "scale", "width": 300})
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/c_scale,"
                              "w_300/sample.jpg?__cld_token__=st=222222222~exp=222222322~hmac"
                              "=55cfe516530461213fe3b3606014533b1eca8ff60aeab79d1bb84c9322eebc1f")

    def test_should_set_url_signature(self):
        cloudinary.config(private_cdn=True)
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", sign_url=True,
                                                 auth_token={"key": ALT_KEY, "start_time": 222222222, "duration": 100,
                                                             "set_url_signature": True},
                                                 type="authenticated", transformation={"crop": "scale", "width": 300})
        self.assertEqual("http://test123-res.cloudinary.com/image/authenticated/s--Ok4O32K7--/"
                         "c_scale,w_300/sample.jpg?__cld_token__=st=222222222~exp=222222322~hmac"
                         "=92a55aaed531b2dab074074bbd1430120119f9cb1b901656925dda2e514a63cc", url)

    def test_should_compute_expiration_as_start_time_plus_duration(self):
        cloudinary.config(private_cdn=True)
        token = {"key": KEY, "start_time": 11111111, "duration": 300}
        url, _ = cloudinary.utils.cloudinary_url("sample.jpg", sign_url=True, auth_token=token, resource_type="image",
                                                 type="authenticated", version="1486020273")
        self.assertEqual(url, "http://test123-res.cloudinary.com/image/authenticated/v1486020273/sample.jpg"
                              "?__cld_token__=st=11111111~exp=11111411~hmac"
                              "=8db0d753ee7bbb9e2eaf8698ca3797436ba4c20e31f44527e43b6a6e995cfdb3")

    def test_generate_token_string(self):
        user = "foobar"  # we can't rely on the default "now" value in tests
        token_options = {"key": KEY, "duration": 300, "acl": "/*/t_%s" % user, "start_time": 222222222}
        cookie_token = cloudinary.utils.generate_auth_token(**token_options)
        self.assertEqual(
            cookie_token,
            "__cld_token__=st=222222222~exp=222222522~acl=%2f*%2ft_foobar~hmac="
            "8e39600cc18cec339b21fe2b05fcb64b98de373355f8ce732c35710d8b10259f"
        )

    def test_generate_token_string_from_string_values(self):
        user = "foobar"
        token_options = {"key": KEY, "duration": "300", "acl": "/*/t_%s" % user, "start_time": "222222222"}
        cookie_token = cloudinary.utils.generate_auth_token(**token_options)
        self.assertEqual(
            cookie_token,
            "__cld_token__=st=222222222~exp=222222522~acl=%2f*%2ft_foobar~hmac="
            "8e39600cc18cec339b21fe2b05fcb64b98de373355f8ce732c35710d8b10259f"
        )

    def test_should_ignore_url_if_acl_is_provided(self):
        token_options = {"key": KEY, "duration": 300, "acl": '/image/*', "start_time": 222222222}
        acl_token = cloudinary.utils.generate_auth_token(**token_options)

        token_options["url"] = "sample.jpg"
        acl_token_url_ignored = cloudinary.utils.generate_auth_token(**token_options)

        self.assertEqual(
            acl_token,
            acl_token_url_ignored
        )

    def test_should_support_multiple_acls(self):
        token_options = {"key": KEY, "duration": 3600,
                         "acl": ["/i/a/*", "/i/a/*", "/i/a/*"],
                         "start_time": 222222222}

        cookie_token = cloudinary.utils.generate_auth_token(**token_options)
        self.assertEqual(
            cookie_token,
            "__cld_token__=st=222222222~exp=222225822~acl=%2fi%2fa%2f*!%2fi%2fa%2f*!"
            "%2fi%2fa%2f*~hmac=10d9ad42d6ed66dce2386c4b564b2aa25a6ac668e5b90d070363a03c9842965f"
        )

    def test_must_provide_expiration_or_duration(self):
        self.assertRaises(Exception, cloudinary.utils.generate_auth_token, acl="*", expiration=None, duration=None)

    def test_must_provide_acl_or_url(self):
        self.assertRaises(Exception, cloudinary.utils.generate_auth_token, start_time=1111111111, duration=300)

    def test_should_support_url_without_acl(self):
        url_token = cloudinary.utils.generate_auth_token(
            start_time=1111111111,
            duration=300,
            url="http://res.cloudinary.com/test123/image/upload/v1486020273/sample.jpg"
        )

        self.assertEqual(
            url_token,
            "__cld_token__=st=1111111111~exp=1111111411~hmac="
            "639406f8c07fc6a1613e1f6192baba631f9d5719185a32049281e94e15c5619b"
        )


if __name__ == '__main__':
    unittest.main()
