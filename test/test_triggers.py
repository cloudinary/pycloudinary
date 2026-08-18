import unittest

from urllib3 import disable_warnings

import cloudinary
from cloudinary import api
from test.helper_test import (
    UNIQUE_TEST_ID, get_uri, get_params, get_method, api_response_mock, get_json_body,
    URLLIB3_REQUEST, patch
)

MOCK_RESPONSE = api_response_mock()

TRIGGER_ID = "trigger_id_{}".format(UNIQUE_TEST_ID)
WEBHOOK_URI = "https://example.com/notifications/{}".format(UNIQUE_TEST_ID)
POLL_CHANNEL_URI = "poll://orders/{}".format(UNIQUE_TEST_ID)
POLL_ANONYMOUS_URI = "poll://*"
LIVE_POLL_URI = "poll://live_{}".format(UNIQUE_TEST_ID)

disable_warnings()


class TriggersTest(unittest.TestCase):
    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_list_triggers(self, mocker):
        """Should list all notification triggers"""
        mocker.return_value = MOCK_RESPONSE

        api.triggers()

        self.assertTrue(get_uri(mocker).endswith("/triggers"))
        self.assertEqual(get_method(mocker), "GET")

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_list_triggers_by_event_type(self, mocker):
        """Should list notification triggers of a single event type"""
        mocker.return_value = MOCK_RESPONSE

        api.triggers(event_type="upload")

        self.assertTrue(get_uri(mocker).endswith("/triggers"))
        self.assertEqual(get_method(mocker), "GET")
        self.assertEqual(get_params(mocker).get("event_type"), "upload")

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test03_create_webhook_trigger(self, mocker):
        """Should create a webhook trigger"""
        mocker.return_value = MOCK_RESPONSE

        api.create_trigger(WEBHOOK_URI, "upload")

        self.assertTrue(get_uri(mocker).endswith("/triggers"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker),
                         {"uri": WEBHOOK_URI, "event_type": "upload", "uri_type": None})

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test04_create_poll_trigger(self, mocker):
        """Should create an anonymous poll trigger"""
        mocker.return_value = MOCK_RESPONSE

        api.create_trigger(POLL_ANONYMOUS_URI, "upload", uri_type="poll")

        self.assertTrue(get_uri(mocker).endswith("/triggers"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "uri": POLL_ANONYMOUS_URI,
            "event_type": "upload",
            "uri_type": "poll",
        })

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_create_poll_channel_trigger(self, mocker):
        """Should create a named channel poll trigger, passing the poll:// URI through"""
        mocker.return_value = MOCK_RESPONSE

        api.create_trigger(POLL_CHANNEL_URI, "all", uri_type="poll")

        self.assertEqual(get_json_body(mocker), {
            "uri": POLL_CHANNEL_URI,
            "event_type": "all",
            "uri_type": "poll",
        })

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_update_trigger(self, mocker):
        """Should update a trigger's destination URI"""
        mocker.return_value = MOCK_RESPONSE

        api.update_trigger(TRIGGER_ID, WEBHOOK_URI)

        self.assertTrue(get_uri(mocker).endswith("/triggers/{}".format(TRIGGER_ID)))
        self.assertEqual(get_method(mocker), "PUT")
        self.assertEqual(get_json_body(mocker), {"new_uri": WEBHOOK_URI})

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08_delete_trigger(self, mocker):
        """Should delete a trigger"""
        mocker.return_value = MOCK_RESPONSE

        api.delete_trigger(TRIGGER_ID)

        self.assertTrue(get_uri(mocker).endswith("/triggers/{}".format(TRIGGER_ID)))
        self.assertEqual(get_method(mocker), "DELETE")
        self.assertEqual(get_json_body(mocker), {})

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09_test_trigger(self, mocker):
        """Should evaluate a trigger's filter against sample data"""
        mocker.return_value = MOCK_RESPONSE

        sample_data = {"notification_type": "upload", "public_id": "sample"}
        api.test_trigger(TRIGGER_ID, sample_data)

        self.assertTrue(get_uri(mocker).endswith("/triggers/{}/test".format(TRIGGER_ID)))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {"sample_data": sample_data})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test10_trigger_lifecycle(self):
        """Should create, list, update and delete a trigger against the live API"""
        created = api.create_trigger(LIVE_POLL_URI, "upload", uri_type="poll")
        trigger_id = created["id"]

        try:
            self.assertEqual(created["uri"], LIVE_POLL_URI)
            self.assertEqual(created["uri_type"], "poll")
            self.assertEqual(created["event_type"], "upload")

            listed = api.triggers()
            self.assertIn(trigger_id, [t["id"] for t in listed["triggers"]])

            api.update_trigger(trigger_id, LIVE_POLL_URI + "_updated")

            updated = [t for t in api.triggers()["triggers"] if t["id"] == trigger_id]
            self.assertEqual(updated[0]["uri"], LIVE_POLL_URI + "_updated")
        finally:
            api.delete_trigger(trigger_id)

        self.assertNotIn(trigger_id, [t["id"] for t in api.triggers()["triggers"]])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test10_test_trigger_without_sample_data(self, mocker):
        """Should send a null sample_data when it is not given; the server treats it as absent"""
        mocker.return_value = MOCK_RESPONSE

        api.test_trigger(TRIGGER_ID)

        self.assertEqual(get_json_body(mocker), {"sample_data": None})


if __name__ == "__main__":
    unittest.main()
