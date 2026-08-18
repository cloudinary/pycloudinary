import hashlib
import json
import time
import unittest

from urllib3 import disable_warnings

import cloudinary
from cloudinary import api, uploader, utils
from test.helper_test import (
    TEST_IMAGE, UNIQUE_TEST_ID, UNIQUE_TAG, get_uri, get_params, get_method, api_response_mock,
    get_json_body, URLLIB3_REQUEST, patch, cleanup_test_resources_by_tag
)

MOCK_RESPONSE = api_response_mock()

BATCH_ID = "batch_{}".format(UNIQUE_TEST_ID)
CHANNEL = "channel_{}".format(UNIQUE_TEST_ID)
RECEIPT_HANDLE = "receipt_handle_{}".format(UNIQUE_TEST_ID)
LIVE_CHANNEL = "live_{}".format(UNIQUE_TEST_ID)

disable_warnings()


def build_message(payload=None, timestamp=None, algorithm=hashlib.sha1, api_secret=None):
    """
    Builds a signed message in the shape the notifications service returns.

    The signature is computed over the byte-exact payload that was signed, which the server
    sends base64url encoded and unpadded in `signed_payload`.
    """
    if payload is None:
        payload = {"notification_type": "upload", "public_id": "sample", "request_id": "req_1"}

    if timestamp is None:
        timestamp = int(time.time())

    timestamp = str(timestamp)

    if api_secret is None:
        api_secret = cloudinary.config().api_secret

    raw = json.dumps(payload, separators=(",", ":"))
    signature = algorithm("{}{}{}".format(raw, timestamp, api_secret).encode("utf-8")).hexdigest()

    return {
        "receipt_handle": RECEIPT_HANDLE,
        "batch_id": BATCH_ID,
        "payload": payload,
        "signed_payload": utils.base64url_encode(raw).rstrip("="),
        "signature": signature,
        "timestamp": timestamp,
    }


class NotificationsTest(unittest.TestCase):
    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_notifications_by_batch_id(self, mocker):
        """Should drain notifications addressed by batch_id from the module-first v2 endpoint"""
        mocker.return_value = MOCK_RESPONSE

        api.notifications(batch_id=BATCH_ID)

        self.assertEqual(get_method(mocker), "GET")
        self.assertTrue(get_uri(mocker).endswith("/v2/notifications/{}/messages".format(
            cloudinary.config().cloud_name)))
        self.assertEqual(get_params(mocker).get("batch_id"), BATCH_ID)
        self.assertIsNone(get_params(mocker).get("channel"))

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_notifications_by_channel(self, mocker):
        """Should drain notifications addressed by channel"""
        mocker.return_value = MOCK_RESPONSE

        api.notifications(channel=CHANNEL)

        self.assertEqual(get_params(mocker).get("channel"), CHANNEL)
        self.assertIsNone(get_params(mocker).get("batch_id"))

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test03_notifications_passes_poll_options(self, mocker):
        """Should pass the poll tuning options through"""
        mocker.return_value = MOCK_RESPONSE

        api.notifications(batch_id=BATCH_ID, max_messages=25, wait_seconds=30,
                          visibility_timeout=60)

        params = get_params(mocker)
        self.assertEqual(params.get("max_messages"), "25")
        self.assertEqual(params.get("wait_seconds"), "30")
        self.assertEqual(params.get("visibility_timeout"), "60")

    def test04_notifications_requires_exactly_one_address(self):
        """Should require exactly one of channel or batch_id, mirroring the server"""
        with self.assertRaises(ValueError):
            api.notifications()

        with self.assertRaises(ValueError):
            api.notifications(channel=CHANNEL, batch_id=BATCH_ID)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_notifications_timeout_from_config(self, mocker):
        """Should take the HTTP timeout from cloudinary.config() when not passed per call"""
        mocker.return_value = MOCK_RESPONSE

        api.notifications(batch_id=BATCH_ID)
        self.assertNotIn("timeout", mocker.call_args[1])

        cloudinary.config(timeout=90)
        try:
            api.notifications(batch_id=BATCH_ID)
            self.assertEqual(mocker.call_args[1]["timeout"], 90)
        finally:
            cloudinary.config(timeout=None)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_notifications_explicit_timeout_wins(self, mocker):
        """Should pass a per-call timeout through untouched, over the configured one"""
        mocker.return_value = MOCK_RESPONSE

        cloudinary.config(timeout=90)
        try:
            api.notifications(batch_id=BATCH_ID, wait_seconds=60, timeout=1)
            self.assertEqual(mocker.call_args[1]["timeout"], 1)
        finally:
            cloudinary.config(timeout=None)

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07_ack_notifications(self, mocker):
        """Should acknowledge a list of receipt handles"""
        mocker.return_value = MOCK_RESPONSE

        api.ack_notifications([RECEIPT_HANDLE, "other_handle"])

        self.assertEqual(get_method(mocker), "POST")
        self.assertTrue(get_uri(mocker).endswith("/v2/notifications/{}/messages/ack".format(
            cloudinary.config().cloud_name)))
        self.assertEqual(get_json_body(mocker),
                         {"receipt_handles": [RECEIPT_HANDLE, "other_handle"]})

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08_ack_notifications_single_handle(self, mocker):
        """Should accept a single receipt handle as a string"""
        mocker.return_value = MOCK_RESPONSE

        api.ack_notifications(RECEIPT_HANDLE)

        self.assertEqual(get_json_body(mocker), {"receipt_handles": [RECEIPT_HANDLE]})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09_verify_signature_of_polled_notification(self):
        """Should verify a polled notification, with the timestamp as a string or an int

        The service sends the timestamp as a string, as does the webhook X-Cld-Timestamp
        header; both forms have to be accepted.
        """
        message = build_message()
        raw = utils.base64url_decode(message["signed_payload"])

        self.assertIsInstance(message["timestamp"], str)
        self.assertTrue(utils.verify_notification_signature(
            raw, message["timestamp"], message["signature"]))
        self.assertTrue(utils.verify_notification_signature(
            raw, int(message["timestamp"]), message["signature"]))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test10_verify_signature_rejects_tampered_payload(self):
        """Should reject a signed payload that was modified after signing"""
        message = build_message()

        raw = utils.base64url_decode(message["signed_payload"]).replace("sample", "evil!!")

        self.assertFalse(utils.verify_notification_signature(
            raw, message["timestamp"], message["signature"]))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test11_verify_signature_rejects_reserialized_payload(self):
        """Should not verify against a re-serialization of the parsed payload

        Signatures cover the byte-exact signed payload, so key order, spacing and escaping all
        have to be preserved - which is why signed_payload exists.
        """
        message = build_message()

        reserialized = json.dumps(message["payload"])

        self.assertNotEqual(reserialized, utils.base64url_decode(message["signed_payload"]))
        self.assertFalse(utils.verify_notification_signature(
            reserialized, message["timestamp"], message["signature"]))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test12_verify_signature_rejects_expired_message(self):
        """Should reject a notification signed longer than valid_for ago"""
        message = build_message(timestamp=int(time.time()) - 10000)
        raw = utils.base64url_decode(message["signed_payload"])

        self.assertFalse(utils.verify_notification_signature(
            raw, message["timestamp"], message["signature"]))
        self.assertTrue(utils.verify_notification_signature(
            raw, message["timestamp"], message["signature"], valid_for=20000))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test13_verify_signature_with_sha256(self):
        """Should verify a notification signed with the configured sha256 algorithm"""
        message = build_message(algorithm=hashlib.sha256)
        raw = utils.base64url_decode(message["signed_payload"])

        self.assertTrue(utils.verify_notification_signature(
            raw, message["timestamp"], message["signature"], algorithm=utils.SIGNATURE_SHA256))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test14_verify_signature_wrong_secret(self):
        """Should reject a notification signed with a different api_secret"""
        message = build_message(api_secret="another_secret")
        raw = utils.base64url_decode(message["signed_payload"])

        self.assertFalse(utils.verify_notification_signature(
            raw, message["timestamp"], message["signature"]))

    def test15_base64url_decode_restores_stripped_padding(self):
        """Should decode the unpadded base64url the server sends, for every payload length"""
        for size in range(1, 6):
            raw = json.dumps({"public_id": "a" * size})
            unpadded = utils.base64url_encode(raw).rstrip("=")

            self.assertEqual(utils.base64url_decode(unpadded), raw)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test16_verify_notification_accepts_the_message(self):
        """Should verify a message envelope directly, decoding signed_payload internally"""
        self.assertTrue(utils.verify_notification(build_message()))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test17_verify_notification_matches_the_manual_two_step(self):
        """Should agree with the verify(base64url_decode(...)) call it replaces

        Pins the helper to the underlying verifier, rather than to a second implementation of
        the same digest.
        """
        for message in (build_message(),
                        build_message(api_secret="another_secret"),
                        build_message(timestamp=int(time.time()) - 10000)):
            expected = utils.verify_notification_signature(
                utils.base64url_decode(message["signed_payload"]),
                message["timestamp"], message["signature"])

            self.assertEqual(utils.verify_notification(message), expected)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test18_verify_notification_rejects_tampered_payload(self):
        """Should reject a message whose signed_payload was modified after signing"""
        message = build_message()
        tampered = utils.base64url_decode(message["signed_payload"]).replace("sample", "evil!!")
        message["signed_payload"] = utils.base64url_encode(tampered).rstrip("=")

        self.assertFalse(utils.verify_notification(message))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test19_verify_notification_passes_through_options(self):
        """Should honor valid_for and algorithm, so the envelope form is not less capable"""
        expired = build_message(timestamp=int(time.time()) - 10000)

        self.assertFalse(utils.verify_notification(expired))
        self.assertTrue(utils.verify_notification(expired, valid_for=20000))

        sha256 = build_message(algorithm=hashlib.sha256)

        self.assertTrue(utils.verify_notification(sha256, algorithm=utils.SIGNATURE_SHA256))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test20_verify_notification_reports_a_missing_key(self):
        """Should raise rather than return False when the envelope is incomplete

        A malformed envelope is a programming error, not a failed signature - returning False
        would report it as a forgery.
        """
        for key in ("signed_payload", "signature", "timestamp"):
            message = build_message()
            del message[key]

            with self.assertRaises(ValueError) as raised:
                utils.verify_notification(message)

            self.assertIn(key, str(raised.exception))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test21_poll_notification_end_to_end(self):
        """Should deliver, verify and acknowledge a real upload notification"""
        trigger = api.create_trigger("poll://" + LIVE_CHANNEL, "upload", uri_type="poll")

        try:
            uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])

            messages = api.notifications(channel=LIVE_CHANNEL,
                                         wait_seconds=20)["messages"]

            self.assertTrue(messages)
            self.assertEqual(messages[0]["payload"]["notification_type"], "upload")
            # For testing purposes only.
            self.assertTrue(utils.verify_notification(messages[0]))

            acked = api.ack_notifications([m["receipt_handle"] for m in messages])

            self.assertEqual([r["status"] for r in acked["results"]],
                             ["acked"] * len(messages))
            self.assertEqual(api.notifications(channel=LIVE_CHANNEL,
                                               wait_seconds=0).get("messages", []), [])
        finally:
            api.delete_trigger(trigger["id"])
            cleanup_test_resources_by_tag([(UNIQUE_TAG,)])


if __name__ == "__main__":
    unittest.main()
