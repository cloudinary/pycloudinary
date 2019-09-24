import unittest

from mock import patch
from urllib3 import disable_warnings

import cloudinary.provisioning.account
from test.helper_test import get_params, provisioning_response_mock

MOCK_RESPONSE = provisioning_response_mock()

disable_warnings()

ACCOUNT_ID = "123415-s1234gdfs-341fd-aga-asdfasdgfasd"
API_KEY = "123415-s1234gdfs-341fd-aga-asdfasdgfasd"
API_SECRET = "123415-s1234gdfs-341fd-aga-asdfasdgfasd"

SUB_ACCOUNT_NAME = "test_subaccount"
SUB_ACCOUNT_ID = "123415-s1234gdfs-341fd-aga-asdfasdgfasd"

NAME = "TestName"
EMAIL = "test@email.com"
USER_ID = "123415-s1234gdfs-341fd-aga-asdfasdgfasd"

CLOUD_NAME = "cloud2019"


class AccountApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.provisioning.account.account_config(**dict(
            account_id=ACCOUNT_ID,
            provisioning_api_key=API_KEY,
            provisioning_api_secret=API_SECRET
        ))

    @classmethod
    def tearDownClass(cls):
        return

    @patch('urllib3.request.RequestMethods.request')
    def test_sub_accounts_params(self, mocker):
        """ should allow ids, enabled, prefix """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.sub_accounts(ids=1, enabled=True)

        params = get_params(mocker.call_args[0])
        self.assertIn("ids", params)
        self.assertIn("enabled", params)

    @patch('urllib3.request.RequestMethods.request')
    def test_create_sub_account(self, mocker):
        """ should allow cloud_name, base_sub_account_id, description """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.create_sub_account(SUB_ACCOUNT_NAME,
                                                           cloud_name=CLOUD_NAME,
                                                           base_sub_account_id=ACCOUNT_ID,
                                                           description="sdk test")

        params = get_params(mocker.call_args[0])
        self.assertIn("cloud_name", params)
        self.assertIn("base_sub_account_id", params)
        self.assertIn("description", params)

    @patch('urllib3.request.RequestMethods.request')
    def test_update_sub_account(self, mocker):
        """ should allow cloud_name, base_sub_account_id, description, enabled """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.update_sub_account(SUB_ACCOUNT_NAME, cloud_name=CLOUD_NAME,
                                                           base_sub_account_id=ACCOUNT_ID,
                                                           description="sdk test", enabled=True)

        params = get_params(mocker.call_args[0])
        self.assertIn("cloud_name", params)
        self.assertIn("base_sub_account_id", params)
        self.assertIn("description", params)
        self.assertIn("enabled", params)

    @patch('urllib3.request.RequestMethods.request')
    def test_update_user_group(self, mocker):
        """ should pass name in params """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.create_sub_account(SUB_ACCOUNT_NAME)

        params = get_params(mocker.call_args[0])
        self.assertIn("name", params)

    @patch('urllib3.request.RequestMethods.request')
    def test_users(self, mocker):
        """ should allow user_ids, sub_account_id, pending, prefix """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.users(user_ids=1, sub_account_id=SUB_ACCOUNT_ID, pending=True, prefix="foobar")

        params = get_params(mocker.call_args[0])
        self.assertIn("user_ids", params)
        self.assertIn("sub_account_id", params)
        self.assertIn("pending", params)
        self.assertIn("prefix", params)

    @patch('urllib3.request.RequestMethods.request')
    def test_create_user(self, mocker):
        """ should pass function arguments in url params """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.create_user(NAME, EMAIL, cloudinary.provisioning.account.Role.ADMIN,
                                                    SUB_ACCOUNT_ID)

        params = get_params(mocker.call_args[0])
        self.assertIn("name", params)
        self.assertIn("email", params)
        self.assertIn("role", params)
        self.assertIn("sub_account_ids", params)

    @patch('urllib3.request.RequestMethods.request')
    def test_update_user(self, mocker):
        """ should pass function arguments in url params """
        mocker.return_value = MOCK_RESPONSE

        cloudinary.provisioning.account.update_user(USER_ID,
                                                    name=NAME,
                                                    email=EMAIL,
                                                    role=cloudinary.provisioning.account.Role.MASTER_ADMIN,
                                                    sub_account_ids=SUB_ACCOUNT_ID,
                                                    enabled=True)

        params = get_params(mocker.call_args[0])
        self.assertIn("name", params)
        self.assertIn("email", params)
        self.assertIn("role", params)
        self.assertIn("sub_account_ids", params)
        self.assertIn("enabled", params)


if __name__ == '__main__':
    unittest.main()
