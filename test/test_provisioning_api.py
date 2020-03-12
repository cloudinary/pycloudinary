import unittest
from datetime import datetime

from urllib3 import disable_warnings

import cloudinary.provisioning.account
from cloudinary.provisioning import account_config, reset_config
from cloudinary.exceptions import AuthorizationRequired

disable_warnings()


class AccountApiTest(unittest.TestCase):
    cloud_id = ""
    user_id = ""
    group_id = ""

    @classmethod
    def setUpClass(cls):
        now = datetime.now().strftime("%m-%d-%Y")
        user_name = "SDK TEST " + now
        user_email = "sdk-test" + now + "@cloudinary.com"
        user_role = "billing"

        reset_config()
        config = account_config()
        if not config.account_id or not config.provisioning_api_key or not config.provisioning_api_secret:
            return

        res = cloudinary.provisioning.create_sub_account("justname" + now, enabled=True)
        cls.cloud_id = res["id"]

        create_user = cloudinary.provisioning.create_user(user_name, user_email, user_role)
        cls.user_id = create_user["id"]

        create_user_group = cloudinary.provisioning.create_user_group("test-group-" + now)
        cls.group_id = create_user_group["id"]

    @classmethod
    def tearDownClass(cls):
        config = account_config()
        if not config.account_id or not config.provisioning_api_key or not config.provisioning_api_secret:
            return
        delete_sub_account = cloudinary.provisioning.delete_sub_account(cls.cloud_id)
        assert delete_sub_account["message"] == "ok"

        delete_user = cloudinary.provisioning.delete_user(cls.user_id)
        assert delete_user["message"] == "ok"

        delete_user_group = cloudinary.provisioning.delete_user_group(cls.group_id)
        assert delete_user_group['ok']

    @unittest.skipUnless(cloudinary.provisioning.account_config().account_id,
                         "requires account_id")
    def test_wrong_api_credentials(self):
        new_name = "This wont be created"
        options = {"provisioning_api_key": "abc", "provisioning_api_secret": "abc"}
        account_config(**options)
        with self.assertRaises(AuthorizationRequired):
            cloudinary.provisioning.create_sub_account(new_name, enabled=True)
        reset_config()

        assert True

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_update_sub_account(self):
        new_name = "new-test-name"
        cloudinary.provisioning.update_sub_account(self.cloud_id, new_name)

        sub_account = cloudinary.provisioning.sub_account(self.cloud_id)
        self.assertEqual(sub_account["name"], new_name)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_all_sub_accounts(self):
        res = cloudinary.provisioning.sub_accounts(True)

        sub_account_by_id = [sub_account for sub_account in res["sub_accounts"]
                             if sub_account["id"] == self.cloud_id]
        self.assertEqual(len(sub_account_by_id), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_specific_sub_account(self):
        res = cloudinary.provisioning.sub_account(self.cloud_id)
        self.assertEqual(res["id"], self.cloud_id)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_update_user(self):
        now = datetime.now().strftime("%m-%d-%Y")
        new_email_address = "updated" + now + "@cloudinary.com"
        new_name = "updated"

        res = cloudinary.provisioning.update_user(self.user_id, new_name, new_email_address)
        self.assertEqual(new_name, res["name"])
        self.assertEqual(new_email_address, res["email"])

        res = cloudinary.provisioning.user(self.user_id)
        self.assertEqual(self.user_id, res["id"])
        self.assertEqual(new_email_address, res["email"])

        res = cloudinary.provisioning.users()
        user_by_id = [user for user in res["users"]
                      if user["id"] == self.user_id]
        self.assertEqual(len(user_by_id), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_users(self):
        res = cloudinary.provisioning.users(user_ids=[self.user_id])
        self.assertEqual(len(res["users"]), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_update_user_group(self):
        now = datetime.now().strftime("%m-%d-%Y")
        new_name = "new-test-name" + now
        res = cloudinary.provisioning.update_user_group(self.group_id, new_name)
        self.assertEqual(res["id"], self.group_id)

        group_data = cloudinary.provisioning.user_group(self.group_id)
        self.assertEqual(group_data["name"], new_name)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_add_remove_user_from_group(self):
        res = cloudinary.provisioning.add_user_to_group(self.group_id, self.user_id)
        self.assertEqual(len(res["users"]), 1)

        group_users_data = cloudinary.provisioning.user_group_users(self.group_id)
        self.assertEqual(len(group_users_data["users"]), 1)

        remove_users_from_group_resp = cloudinary.provisioning.remove_user_from_group(self.group_id,
                                                                                      self.user_id)
        self.assertEqual(len(remove_users_from_group_resp["users"]), 0)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_user_groups(self):
        res = cloudinary.provisioning.user_groups()
        group_by_id = [user_group for user_group in res["user_groups"]
                       if user_group["id"] == self.group_id]

        self.assertEqual(len(group_by_id), 1)
        # Ensure we can find our ID in the list(Which means we got a real list as a response)
        self.assertEqual(group_by_id[0]["id"], self.group_id)


if __name__ == '__main__':
    unittest.main()
