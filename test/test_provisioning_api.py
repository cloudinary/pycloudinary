import unittest
from datetime import datetime

import six
from urllib3 import disable_warnings

import cloudinary.provisioning.account
from cloudinary.provisioning import account_config, reset_config
from cloudinary.exceptions import AuthorizationRequired, NotFound

from test.helper_test import UNIQUE_SUB_ACCOUNT_ID, UNIQUE_TEST_ID

disable_warnings()


class AccountApiTest(unittest.TestCase):
    cloud_id = ""
    user_id = ""
    group_id = ""

    @classmethod
    def setUpClass(cls):
        now = datetime.now().strftime("%m-%d-%Y")
        cls.user_name_1 = "SDK TEST " + now
        cls.user_name_2 = "SDK TEST 2 " + now
        user_email_1 = "sdk-test" + now + "@cloudinary.com"
        user_email_2 = "sdk-test2" + now + "@cloudinary.com"
        user_role = "billing"

        reset_config()
        config = account_config()
        if not config.account_id or not config.provisioning_api_key or not config.provisioning_api_secret:
            return

        create_sub_account_res = cloudinary.provisioning.create_sub_account("justname" + now, enabled=True)
        cls.cloud_id = create_sub_account_res["id"]

        create_user_1 = cloudinary.provisioning.create_user(cls.user_name_1, user_email_1, user_role)
        cls.user_id_1 = create_user_1["id"]

        create_user_2 = cloudinary.provisioning.create_user(cls.user_name_2, user_email_2, user_role)
        cls.user_id_2 = create_user_2["id"]

        create_user_group = cloudinary.provisioning.create_user_group("test-group-" + now)
        cls.group_id = create_user_group["id"]

    @classmethod
    def tearDownClass(cls):
        config = account_config()
        if not config.account_id or not config.provisioning_api_key or not config.provisioning_api_secret:
            return
        delete_sub_account = cloudinary.provisioning.delete_sub_account(cls.cloud_id)
        assert delete_sub_account["message"] == "ok"

        delete_user_1 = cloudinary.provisioning.delete_user(cls.user_id_1)
        assert delete_user_1["message"] == "ok"

        delete_user_2 = cloudinary.provisioning.delete_user(cls.user_id_2)
        assert delete_user_2["message"] == "ok"

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

        res = cloudinary.provisioning.update_user(self.user_id_1, new_name, new_email_address)
        self.assertEqual(new_name, res["name"])
        self.assertEqual(new_email_address, res["email"])

        res = cloudinary.provisioning.user(self.user_id_1)
        self.assertEqual(self.user_id_1, res["id"])
        self.assertEqual(new_email_address, res["email"])

        res = cloudinary.provisioning.users()
        user_by_id = [user for user in res["users"]
                      if user["id"] == self.user_id_1]
        self.assertEqual(len(user_by_id), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_users(self):
        res = cloudinary.provisioning.users(user_ids=[self.user_id_1])
        self.assertEqual(len(res["users"]), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_pending_users(self):
        res = cloudinary.provisioning.users(user_ids=[self.user_id_1], pending=True)
        self.assertEqual(len(res["users"]), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_non_pending_users(self):
        res = cloudinary.provisioning.users(user_ids=[self.user_id_1], pending=False)
        self.assertEqual(len(res["users"]), 0)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_pending_and_non_pending_users(self):
        res = cloudinary.provisioning.users(user_ids=[self.user_id_1], pending=None)
        self.assertEqual(len(res["users"]), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_users_by_prefix(self):
        res_1 = cloudinary.provisioning.users(pending=True, prefix=self.user_name_2[:-1])
        res_2 = cloudinary.provisioning.users(pending=True, prefix=self.user_name_2+'zzz')
        self.assertEqual(len(res_1["users"]), 1)
        self.assertEqual(len(res_2["users"]), 0)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_users_by_sub_account_id(self):
        res = cloudinary.provisioning.users(pending=True, user_ids=[self.user_id_2], sub_account_id=self.cloud_id)
        self.assertEqual(len(res["users"]), 1)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_users_by_nonexistent_sub_account_id(self):
        with six.assertRaisesRegex(self, NotFound, "Cannot find sub account with id {}".format(UNIQUE_SUB_ACCOUNT_ID)):
            cloudinary.provisioning.users(pending=True, sub_account_id=UNIQUE_SUB_ACCOUNT_ID)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_users_by_login(self):
        res = cloudinary.provisioning.users(user_ids=[self.user_id_1], pending=None, 
                                            last_login="true", from_date=datetime.today(), to_date=datetime.today())
        self.assertEqual(len(res["users"]), 0)

        res = cloudinary.provisioning.users(user_ids=[self.user_id_1], pending=None,
                                            last_login="false", from_date=datetime.today(), to_date=datetime.today())
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
        res = cloudinary.provisioning.add_user_to_group(self.group_id, self.user_id_1)
        self.assertEqual(len(res["users"]), 1)

        group_users_data = cloudinary.provisioning.user_group_users(self.group_id)
        self.assertEqual(len(group_users_data["users"]), 1)

        remove_users_from_group_resp = cloudinary.provisioning.remove_user_from_group(self.group_id,
                                                                                      self.user_id_1)
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

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_get_access_keys(self):
        res = cloudinary.provisioning.access_keys(self.cloud_id)

        self.assertGreater(res["total"], 0)
        self.assertGreater(len(res["access_keys"]), 0)

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_generate_access_key(self):
        key_name = UNIQUE_TEST_ID + "_test_key"
        res = cloudinary.provisioning.generate_access_key(self.cloud_id, name=key_name, enabled=False)

        self.assertEqual(key_name, res["name"])
        self.assertEqual(False, res["enabled"])

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_update_access_key(self):
        key_name = UNIQUE_TEST_ID + "_before_update_test_key"
        updated_key_name = UNIQUE_TEST_ID + "_updated_test_key"

        key_res = cloudinary.provisioning.generate_access_key(self.cloud_id, name=key_name, enabled=False)

        self.assertEqual(key_name, key_res["name"])
        self.assertEqual(False, key_res["enabled"])

        res = cloudinary.provisioning.update_access_key(self.cloud_id, key_res["api_key"],
                                                        name=updated_key_name, enabled=True, dedicated_for="webhooks")

        self.assertEqual(updated_key_name, res["name"])
        self.assertEqual(True, res["enabled"])
        self.assertEqual(1, len(res["dedicated_for"]))
        self.assertEqual("webhooks", res["dedicated_for"][0])

    @unittest.skipUnless(cloudinary.provisioning.account_config().provisioning_api_secret,
                         "requires provisioning_api_key/provisioning_api_secret")
    def test_delete_access_key(self):
        key_name = UNIQUE_TEST_ID + "_delete_key"
        named_key_name = UNIQUE_TEST_ID + "_delete_by_name_key"

        key_res = cloudinary.provisioning.generate_access_key(self.cloud_id, name=key_name, enabled=True)
        self.assertEqual(key_name, key_res["name"])
        self.assertEqual(True, key_res["enabled"])

        named_key_res = cloudinary.provisioning.generate_access_key(self.cloud_id, name=named_key_name, enabled=True)
        self.assertEqual(named_key_name, named_key_res["name"])
        self.assertEqual(True, named_key_res["enabled"])

        key_del_res = cloudinary.provisioning.delete_access_key(self.cloud_id, named_key_res["api_key"])
        self.assertEqual("ok", key_del_res["message"])

        named_key_del_res = cloudinary.provisioning.delete_access_key(self.cloud_id, name=key_name)
        self.assertEqual("ok", named_key_del_res["message"])


if __name__ == '__main__':
    unittest.main()
