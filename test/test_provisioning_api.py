import json
import unittest
from datetime import datetime

import six
from urllib3 import disable_warnings

import cloudinary.provisioning.account
from cloudinary.provisioning import account_config, reset_config
from cloudinary.exceptions import AuthorizationRequired, BadRequest, NotFound, RateLimited

from test.helper_test import (UNIQUE_SUB_ACCOUNT_ID, UNIQUE_TEST_ID, URLLIB3_REQUEST, patch, api_response_mock,
                              http_response_mock, get_uri, get_method, get_params, get_headers)

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


class CreateAgentAccountTest(unittest.TestCase):
    """
    The create agent account endpoint is public, unauthenticated and rate limited per IP,
    so it is verified against a mocked transport rather than the live API.
    """

    def test_create_agent_account(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_agent_account(
                "jane@example.com",
                agent_framework="langchain",
                agent_llm_model="claude-opus-4-8",
                agent_goal="Build a product image gallery",
                sdk_framework="python",
            )

        self.assertEqual("POST", get_method(mocker))
        self.assertTrue(get_uri(mocker).endswith("/provisioning/agents/accounts"))

        params = get_params(mocker)
        self.assertEqual("jane@example.com", params["email"])
        self.assertEqual("langchain", params["agent_framework"])
        self.assertEqual("claude-opus-4-8", params["agent_llm_model"])
        self.assertEqual("Build a product image gallery", params["agent_goal"])
        self.assertEqual("python", params["sdk_framework"])

    def test_create_agent_account_is_unauthenticated(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_agent_account(
                "jane@example.com",
                agent_framework="langchain",
                agent_llm_model="claude-opus-4-8",
                agent_goal="Build a product image gallery",
            )

        # The endpoint is public - no authorization header must be sent.
        headers = get_headers(mocker)
        self.assertNotIn("authorization", {k.lower() for k in headers})

    def test_create_agent_account_omits_unset_sdk_framework(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_agent_account(
                "jane@example.com",
                agent_framework="langchain",
                agent_llm_model="claude-opus-4-8",
                agent_goal="Build a product image gallery",
            )

        self.assertNotIn("sdk_framework", get_params(mocker))

    def test_create_agent_account_parses_response(self):
        body = json.dumps({
            "external_id": "0aaaaa1bbbbb2ccccc3ddddd4eeeee5f",
            "email": "jane@example.com",
            "plan_name": "free",
            "product_environments": [{
                "external_id": "abcde1fghij2klmno3pqrst4uvwxy5z",
                "cloud_name": "product1",
                "api_key": "123456789012345",
                "api_secret": "asdf1JKL2xyz3ABc4s3c5reT01DfaKez",
                "api_environment_variable":
                    "CLOUDINARY_URL=cloudinary://123456789012345:asdf1JKL2xyz3ABc4s3c5reT01DfaKez@product1",
            }],
            "guidance": "A verification email has been sent to the supplied email address.",
        })
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock(body)
            res = cloudinary.provisioning.create_agent_account(
                "jane@example.com",
                agent_framework="langchain",
                agent_llm_model="claude-opus-4-8",
                agent_goal="Build a product image gallery",
            )

        self.assertEqual("free", res["plan_name"])
        self.assertEqual("jane@example.com", res["email"])
        self.assertEqual(1, len(res["product_environments"]))
        product_environment = res["product_environments"][0]
        self.assertEqual("product1", product_environment["cloud_name"])
        self.assertEqual("123456789012345", product_environment["api_key"])
        self.assertEqual("asdf1JKL2xyz3ABc4s3c5reT01DfaKez", product_environment["api_secret"])
        self.assertIn("CLOUDINARY_URL=cloudinary://", product_environment["api_environment_variable"])
        self.assertIn("guidance", res)


class CreateCloudTest(unittest.TestCase):
    """
    The create cloud endpoint is public, unauthenticated and rate limited per IP, and every
    successful call provisions a real account, so it is verified against a mocked transport
    rather than the live API.
    """

    def test_create_cloud(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud()

        self.assertEqual("POST", get_method(mocker))
        uri = get_uri(mocker)
        self.assertTrue(uri.endswith("/provisioning/clouds"))
        # The resource sits directly under provisioning/, with no agents/ prefix and no
        # accounts/{account_id} segment.
        self.assertNotIn("/agents", uri)
        self.assertNotIn("/accounts", uri)

    def test_create_cloud_is_unauthenticated(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud()

        # The endpoint is public - no authorization header must be sent.
        headers = get_headers(mocker)
        self.assertNotIn("authorization", {k.lower() for k in headers})

    def test_create_cloud_omits_unset_delivery_ips(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud()

        # The default path sends no delivery_ips at all, letting the server derive the
        # allow-list from the requester's own resolved address.
        self.assertNotIn("delivery_ips", get_params(mocker))
        # Nothing else is sent either - an empty body is the documented default request.
        self.assertEqual({}, get_params(mocker))

    def test_create_cloud_sends_requester_ip_sentinel(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud(["requester_ip"])

        # Passed through verbatim; the server substitutes its own resolved address.
        self.assertEqual(["requester_ip"], get_params(mocker)["delivery_ips"])

    def test_create_cloud_sends_delivery_ips_as_array(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud(["8.8.8.8", "1.1.1.1", "requester_ip"])

        # The server rejects a comma-joined string with "delivery_ips must be an array of
        # IP addresses", so the list must stay a genuine array on the wire.
        self.assertEqual(["8.8.8.8", "1.1.1.1", "requester_ip"], get_params(mocker)["delivery_ips"])

    def test_create_cloud_sends_optional_email(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud(email="jane@example.com")

        self.assertEqual("jane@example.com", get_params(mocker)["email"])

    def test_create_cloud_omits_unset_email(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud(["8.8.8.8"])

        # Omitted rather than sent empty: the server generates a placeholder address.
        self.assertNotIn("email", get_params(mocker))

    def test_create_cloud_sends_optional_agent_metadata(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud(
                agent_framework="langchain",
                agent_llm_model="claude-opus-5",
                agent_goal="Build a product image gallery",
                sdk_framework="python",
            )

        params = get_params(mocker)
        self.assertEqual("langchain", params["agent_framework"])
        self.assertEqual("claude-opus-5", params["agent_llm_model"])
        self.assertEqual("Build a product image gallery", params["agent_goal"])
        self.assertEqual("python", params["sdk_framework"])

    def test_create_cloud_omits_unset_agent_metadata(self):
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock()
            cloudinary.provisioning.create_cloud()

        params = get_params(mocker)
        for field in ("agent_framework", "agent_llm_model", "agent_goal", "sdk_framework"):
            self.assertNotIn(field, params)

    def test_create_cloud_parses_response(self):
        body = json.dumps({
            "account_id": "00000000-0000-0000-0000-000000000000",
            "email": "cloud-0000000000000000@cloud.cloudinary.invalid",
            "cloud_name": "test-cloud",
            "api_key": "000000000000000",
            "api_secret": "FAKE_API_SECRET_FOR_TESTS",
            "api_environment_variable":
                "CLOUDINARY_URL=cloudinary://000000000000000:FAKE_API_SECRET_FOR_TESTS@test-cloud",
            "claimed": False,
            "expires_at": "2026-08-13T13:08:42Z",
            "delivery_ips": ["8.8.8.8"],
            "claim_url": "https://console.cloudinary.com/users/agent_email_confirmation?token=FAKE_CLAIM_TOKEN",
            "guidance": "A Claimable Cloud is ready and the API key and secret below work immediately.",
        })
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock(body)
            res = cloudinary.provisioning.create_cloud(["8.8.8.8"])

        self.assertEqual("00000000-0000-0000-0000-000000000000", res["account_id"])
        self.assertEqual("test-cloud", res["cloud_name"])
        self.assertEqual("000000000000000", res["api_key"])
        self.assertEqual("FAKE_API_SECRET_FOR_TESTS", res["api_secret"])
        self.assertIn("CLOUDINARY_URL=cloudinary://", res["api_environment_variable"])
        self.assertFalse(res["claimed"])
        self.assertEqual("2026-08-13T13:08:42Z", res["expires_at"])
        self.assertEqual(["8.8.8.8"], res["delivery_ips"])
        self.assertIn("agent_email_confirmation", res["claim_url"])
        self.assertIn("guidance", res)

    def test_create_cloud_passes_through_unknown_response_shape(self):
        # The contracted response is flat, but it is returned verbatim rather than reshaped,
        # so unrecognized or added fields (here credentials nested under
        # product_environments[], the shape the agent-account endpoint uses) still reach the
        # caller intact instead of being dropped.
        body = json.dumps({
            "id": "00000000-0000-0000-0000-000000000000",
            "email": "cloud-0000000000000000@cloud.cloudinary.invalid",
            "expires_at": "2026-08-13T13:08:42Z",
            "delivery_ips": ["8.8.8.8"],
            "claim_url": "https://console.cloudinary.com/users/agent_email_confirmation?token=FAKE_CLAIM_TOKEN",
            "product_environments": [{
                "cloud_name": "test-cloud",
                "api_access_keys": [{"key": "000000000000000",
                                     "secret": "FAKE_API_SECRET_FOR_TESTS",
                                     "enabled": True}],
            }],
        })
        with patch(URLLIB3_REQUEST) as mocker:
            mocker.return_value = api_response_mock(body)
            res = cloudinary.provisioning.create_cloud(["8.8.8.8"])

        product_environment = res["product_environments"][0]
        self.assertEqual("test-cloud", product_environment["cloud_name"])
        self.assertEqual("000000000000000", product_environment["api_access_keys"][0]["key"])
        self.assertEqual("FAKE_API_SECRET_FOR_TESTS", product_environment["api_access_keys"][0]["secret"])

    def test_create_cloud_maps_errors(self):
        for status, code in ((400, "delivery_ips_not_public"),
                             (400, "delivery_ips_invalid"),
                             (400, "delivery_ips_too_many")):
            body = json.dumps({"error": {"category": "invalid_parameter",
                                         "code": code,
                                         "message": "delivery_ips error"}})
            with patch(URLLIB3_REQUEST) as mocker:
                mocker.return_value = http_response_mock(body, status=status)
                with self.assertRaises(BadRequest):
                    cloudinary.provisioning.create_cloud(["not-an-ip"])

        for status in (420, 429):
            body = json.dumps({"error": {"category": "rate_limit",
                                         "code": "ip_rate_limit_exceeded",
                                         "message": "Rate limit exceeded"}})
            with patch(URLLIB3_REQUEST) as mocker:
                mocker.return_value = http_response_mock(body, status=status)
                with self.assertRaises(RateLimited):
                    cloudinary.provisioning.create_cloud(["8.8.8.8"])


if __name__ == '__main__':
    unittest.main()
