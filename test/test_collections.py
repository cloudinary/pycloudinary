import json
import unittest

import six
from urllib3 import disable_warnings

import cloudinary
from cloudinary import api, collections, utils
from test.helper_test import (
    UNIQUE_TEST_ID, get_uri, get_params, get_method, get_headers, get_json_body, api_response_mock,
    http_response_mock, URLLIB3_REQUEST, patch
)
from cloudinary.exceptions import BadRequest, Error, Locked, NotAcceptable, NotFound

MOCK_RESPONSE = api_response_mock()

COLLECTION_ID = "col_{}".format(UNIQUE_TEST_ID)
PUBLIC_PAGE_ID = "pub_{}".format(UNIQUE_TEST_ID)
ASSET_IDS = ["ast_1_{}".format(UNIQUE_TEST_ID), "ast_2_{}".format(UNIQUE_TEST_ID)]

CUSTOMER_ID_HEADER = "X-Cld-Customer-External-Id"
CUSTOMER_ID = "cust_{}".format(UNIQUE_TEST_ID)

disable_warnings()


def build_jwt(claims):
    return ".".join(["e30", utils.base64url_encode(json.dumps(claims)).rstrip("="), "sig"])


OAUTH_TOKEN_WITH_CUSTOMER_ID = build_jwt({"ext": {"customer_external_id": CUSTOMER_ID}})


def collections_uri(*path):
    return "/".join(["/v2/asset_management", cloudinary.config().cloud_name, "collections"] + list(path))


@unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
class CollectionsTest(unittest.TestCase):
    def assertRequest(self, mocker, method, *path):
        self.assertEqual(get_method(mocker), method)
        self.assertEqual(get_uri(mocker), collections_uri(*path))

    @patch(URLLIB3_REQUEST)
    def test01_collections(self, mocker):
        """Should list collections with query, sort and paging params"""
        mocker.return_value = MOCK_RESPONSE

        collections.collections(query="summer", sort_by="name asc", max_results=10, next_cursor="abc")

        self.assertRequest(mocker, "GET")
        self.assertEqual(get_params(mocker),
                         {"query": "summer", "sort_by": "name asc", "max_results": "10", "next_cursor": "abc"})

    @patch(URLLIB3_REQUEST)
    def test02_create_collection(self, mocker):
        """Should create a dynamic collection"""
        mocker.return_value = MOCK_RESPONSE

        configuration = {"expression": "tags=summer"}
        collections.create_collection("Summer", description="desc", type="dynamic", configuration=configuration)

        self.assertRequest(mocker, "POST")
        self.assertEqual(get_json_body(mocker), {"name": "Summer", "description": "desc", "type": "dynamic",
                                                 "configuration": configuration})

    @patch(URLLIB3_REQUEST)
    def test03_collection(self, mocker):
        """Should get a collection"""
        mocker.return_value = MOCK_RESPONSE

        collections.collection(COLLECTION_ID)

        self.assertRequest(mocker, "GET", COLLECTION_ID)

    @patch(URLLIB3_REQUEST)
    def test04_update_collection(self, mocker):
        """Should send only the passed fields when updating a collection"""
        mocker.return_value = MOCK_RESPONSE

        collections.update_collection(COLLECTION_ID, name="Renamed", type="manual")

        self.assertRequest(mocker, "PUT", COLLECTION_ID)
        self.assertEqual(get_json_body(mocker), {"name": "Renamed"})

    @patch(URLLIB3_REQUEST)
    def test05_update_collection_explicit_none(self, mocker):
        """Should send an explicitly passed None as null"""
        mocker.return_value = MOCK_RESPONSE

        collections.update_collection(COLLECTION_ID, description=None)

        self.assertEqual(get_json_body(mocker), {"description": None})

    @patch(URLLIB3_REQUEST)
    def test06_delete_collection(self, mocker):
        """Should delete a collection"""
        mocker.return_value = MOCK_RESPONSE

        collections.delete_collection(COLLECTION_ID)

        self.assertRequest(mocker, "DELETE", COLLECTION_ID)

    @patch(URLLIB3_REQUEST)
    def test07_collection_assets(self, mocker):
        """Should list the assets of a collection with sort and paging params"""
        mocker.return_value = MOCK_RESPONSE

        collections.collection_assets(COLLECTION_ID, sort_by="bytes desc", max_results=5, next_cursor="abc")

        self.assertRequest(mocker, "GET", COLLECTION_ID, "assets")
        self.assertEqual(get_params(mocker), {"sort_by": "bytes desc", "max_results": "5", "next_cursor": "abc"})

    @patch(URLLIB3_REQUEST)
    def test08_add_collection_assets(self, mocker):
        """Should add assets to a collection as a bare JSON array"""
        mocker.return_value = MOCK_RESPONSE

        collections.add_collection_assets(COLLECTION_ID, ASSET_IDS)

        self.assertRequest(mocker, "POST", COLLECTION_ID, "assets")
        self.assertEqual(get_json_body(mocker), ASSET_IDS)

    @patch(URLLIB3_REQUEST)
    def test09_add_collection_asset_string(self, mocker):
        """Should wrap a single asset ID in a list"""
        mocker.return_value = MOCK_RESPONSE

        collections.add_collection_assets(COLLECTION_ID, ASSET_IDS[0])

        self.assertEqual(get_json_body(mocker), [ASSET_IDS[0]])

    @patch(URLLIB3_REQUEST)
    def test10_remove_collection_assets(self, mocker):
        """Should remove assets from a collection as a bare JSON array"""
        mocker.return_value = MOCK_RESPONSE

        collections.remove_collection_assets(COLLECTION_ID, ASSET_IDS)

        self.assertRequest(mocker, "DELETE", COLLECTION_ID, "assets")
        self.assertEqual(get_json_body(mocker), ASSET_IDS)

    @patch(URLLIB3_REQUEST)
    def test11_create_collection_public_page(self, mocker):
        """Should publish a collection, dropping update-only fields"""
        mocker.return_value = MOCK_RESPONSE

        transformations = [{"name": "thumbnail_400", "types": ["image"]}]
        collections.create_collection_public_page(COLLECTION_ID, name="Preview",
                                                  available_from="2026-03-20T00:00:00Z",
                                                  expires_at="2026-04-20T00:00:00Z",
                                                  show_download_original_option=True,
                                                  download_transformations=transformations,
                                                  create_download_transformations=True,
                                                  protection_mode="email_otp")

        self.assertRequest(mocker, "POST", COLLECTION_ID, "public_pages")
        self.assertEqual(get_json_body(mocker), {"name": "Preview",
                                                 "available_from": "2026-03-20T00:00:00Z",
                                                 "expires_at": "2026-04-20T00:00:00Z",
                                                 "show_download_original_option": True,
                                                 "download_transformations": transformations,
                                                 "create_download_transformations": True})

    @patch(URLLIB3_REQUEST)
    def test12_collection_public_pages(self, mocker):
        """Should list the public pages of a collection"""
        mocker.return_value = MOCK_RESPONSE

        collections.collection_public_pages(COLLECTION_ID)

        self.assertRequest(mocker, "GET", COLLECTION_ID, "public_pages")

    @patch(URLLIB3_REQUEST)
    def test13_collection_public_page(self, mocker):
        """Should get a public page of a collection"""
        mocker.return_value = MOCK_RESPONSE

        collections.collection_public_page(COLLECTION_ID, PUBLIC_PAGE_ID)

        self.assertRequest(mocker, "GET", COLLECTION_ID, "public_pages", PUBLIC_PAGE_ID)

    @patch(URLLIB3_REQUEST)
    def test14_update_collection_public_page(self, mocker):
        """Should update the protection settings of a public page"""
        mocker.return_value = MOCK_RESPONSE

        collections.update_collection_public_page(COLLECTION_ID, PUBLIC_PAGE_ID, name="Press kit",
                                                  protection_mode="email_otp",
                                                  allowed_emails=["alice@example.com"],
                                                  allowed_domains=["example.com"], allow_any=False,
                                                  custom_layout_url="https://example.com/layout")

        self.assertRequest(mocker, "PUT", COLLECTION_ID, "public_pages", PUBLIC_PAGE_ID)
        self.assertEqual(get_json_body(mocker), {"name": "Press kit",
                                                 "protection_mode": "email_otp",
                                                 "allowed_emails": ["alice@example.com"],
                                                 "allowed_domains": ["example.com"],
                                                 "allow_any": False,
                                                 "custom_layout_url": "https://example.com/layout"})

    @patch(URLLIB3_REQUEST)
    def test15_delete_collection_public_page(self, mocker):
        """Should unpublish a public page of a collection"""
        mocker.return_value = MOCK_RESPONSE

        collections.delete_collection_public_page(COLLECTION_ID, PUBLIC_PAGE_ID)

        self.assertRequest(mocker, "DELETE", COLLECTION_ID, "public_pages", PUBLIC_PAGE_ID)


class CollectionsCustomerIdTest(unittest.TestCase):
    def setUp(self):
        self.config = cloudinary.config()
        self.config.cloud_name = self.config.cloud_name or "test-cloud"

    def tearDown(self):
        self.config.oauth_token = None

    @patch(URLLIB3_REQUEST)
    def test01_customer_id_header_from_oauth_option(self, mocker):
        """Should send the customer ID from the OAuth token passed as an option"""
        mocker.return_value = MOCK_RESPONSE

        collections.collections(oauth_token=OAUTH_TOKEN_WITH_CUSTOMER_ID)

        self.assertEqual(get_headers(mocker)[CUSTOMER_ID_HEADER], CUSTOMER_ID)
        self.assertEqual(get_headers(mocker)["authorization"], "Bearer " + OAUTH_TOKEN_WITH_CUSTOMER_ID)

    @patch(URLLIB3_REQUEST)
    def test02_customer_id_header_from_oauth_config(self, mocker):
        """Should send the customer ID from the OAuth token in the config"""
        mocker.return_value = MOCK_RESPONSE
        self.config.oauth_token = OAUTH_TOKEN_WITH_CUSTOMER_ID

        collections.add_collection_assets(COLLECTION_ID, ASSET_IDS)

        self.assertEqual(get_headers(mocker)[CUSTOMER_ID_HEADER], CUSTOMER_ID)

    @patch(URLLIB3_REQUEST)
    def test03_customer_id_header_not_sent_with_key_secret(self, mocker):
        """Should not send the customer ID with API key and secret"""
        mocker.return_value = MOCK_RESPONSE

        collections.collections(api_key="key", api_secret="secret")

        self.assertNotIn(CUSTOMER_ID_HEADER, get_headers(mocker))

    @patch(URLLIB3_REQUEST)
    def test04_customer_id_header_not_sent_outside_collections(self, mocker):
        """Should not send the customer ID on other APIs"""
        mocker.return_value = MOCK_RESPONSE

        api.ping(oauth_token=OAUTH_TOKEN_WITH_CUSTOMER_ID)

        self.assertNotIn(CUSTOMER_ID_HEADER, get_headers(mocker))

    @patch(URLLIB3_REQUEST)
    def test05_customer_id_header_not_sent_without_claim(self, mocker):
        """Should not send the customer ID when the token has no usable claim"""
        mocker.return_value = MOCK_RESPONSE

        tokens = [build_jwt({}), build_jwt({"ext": {}}), build_jwt({"ext": {"customer_external_id": ""}}),
                  build_jwt({"ext": {"customer_external_id": 123}}), build_jwt({"ext": "x"}), build_jwt([]),
                  "not-a-jwt", "a.!!!.c", "a.e30"]
        for token in tokens:
            collections.collections(oauth_token=token)

            self.assertNotIn(CUSTOMER_ID_HEADER, get_headers(mocker), token)

    @patch(URLLIB3_REQUEST)
    def test06_customer_id_header_from_caller_kept(self, mocker):
        """Should keep a customer ID header passed by the caller"""
        mocker.return_value = MOCK_RESPONSE

        collections.collections(oauth_token=OAUTH_TOKEN_WITH_CUSTOMER_ID,
                                extra_headers={CUSTOMER_ID_HEADER: "explicit"})

        self.assertEqual(get_headers(mocker)[CUSTOMER_ID_HEADER], "explicit")


class CollectionsErrorsTest(unittest.TestCase):
    def setUp(self):
        self.config = cloudinary.config()
        self.config.cloud_name = self.config.cloud_name or "test-cloud"

    @patch(URLLIB3_REQUEST)
    def test01_error_code_and_message_raises(self, mocker):
        """Should raise on an error response with error_code and message"""
        mocker.return_value = http_response_mock('{"error_code":"not_found","message":"No such collection"}',
                                                 status=404)

        with six.assertRaisesRegex(self, NotFound, "Error 404 - No such collection"):
            collections.collection(COLLECTION_ID, api_key="key", api_secret="secret")

    @patch(URLLIB3_REQUEST)
    def test02_message_only_raises(self, mocker):
        """Should raise on an error response with only a message"""
        mocker.return_value = http_response_mock('{"message":"invalid type"}', status=400)

        with six.assertRaisesRegex(self, BadRequest, "Error 400 - invalid type"):
            collections.create_collection("x", type="bogus", api_key="key", api_secret="secret")

    @patch(URLLIB3_REQUEST)
    def test03_success_message_returned(self, mocker):
        """Should return a successful response that carries a message"""
        mocker.return_value = http_response_mock('{"message":"Collection deleted successfully."}', status=200)

        result = collections.delete_collection(COLLECTION_ID, api_key="key", api_secret="secret")

        self.assertEqual(result["message"], "Collection deleted successfully.")

    @patch(URLLIB3_REQUEST)
    def test04_legacy_error_shape_unchanged(self, mocker):
        """Should keep raising on the error object shape"""
        mocker.return_value = http_response_mock('{"error":{"message":"Resource not found"}}', status=404)

        with six.assertRaisesRegex(self, NotFound, "Error 404 - Resource not found"):
            api.ping(api_key="key", api_secret="secret")


    @patch(URLLIB3_REQUEST)
    def test05_not_acceptable_raises(self, mocker):
        """Should raise NotAcceptable on 406"""
        mocker.return_value = http_response_mock('{"message":"unsupported operation for dynamic collection"}',
                                                 status=406)

        with six.assertRaisesRegex(self, NotAcceptable, "Error 406 - unsupported operation"):
            collections.add_collection_assets(COLLECTION_ID, ASSET_IDS, api_key="key", api_secret="secret")

    @patch(URLLIB3_REQUEST)
    def test06_locked_raises(self, mocker):
        """Should raise Locked on 423"""
        mocker.return_value = http_response_mock('{"error":{"message":"Resource is being processed"}}', status=423)

        with six.assertRaisesRegex(self, Locked, "Error 423 - Resource is being processed"):
            api.ping(api_key="key", api_secret="secret")

    @patch(URLLIB3_REQUEST)
    def test07_unmapped_status_raises_error(self, mocker):
        """Should raise the base Error on an unmapped status"""
        mocker.return_value = http_response_mock('{"message":"I\'m a teapot"}', status=418)

        with self.assertRaises(Error) as context:
            collections.collections(api_key="key", api_secret="secret")

        self.assertIs(type(context.exception), Error)


if __name__ == '__main__':
    unittest.main()
