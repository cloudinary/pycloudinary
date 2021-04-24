import unittest

import six

import cloudinary
from cloudinary import api
from cloudinary.exceptions import AuthorizationRequired
from test.helper_test import UNIQUE_TEST_ID

FAKE_OAUTH_TOKEN = 'MTQ0NjJkZmQ5OTM2NDE1ZTZjNGZmZjI4'
UNIQUE_IMAGE_PUBLIC_ID = 'asset_image_{}'.format(UNIQUE_TEST_ID)


class OAuthTest(unittest.TestCase):
    def test_oauth_token(self):
        config = cloudinary.config()
        config.oauth_token = FAKE_OAUTH_TOKEN

        with six.assertRaisesRegex(self, AuthorizationRequired, "Invalid token"):
            api.resource(UNIQUE_IMAGE_PUBLIC_ID)


if __name__ == '__main__':
    unittest.main()
