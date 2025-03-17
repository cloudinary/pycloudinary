import unittest
from six import text_type
from urllib3 import disable_warnings

import cloudinary
from cloudinary import api
from cloudinary.exceptions import BadRequest, NotFound
from test.helper_test import (
    UNIQUE_TEST_ID, get_uri, get_params, get_method, api_response_mock, ignore_exception, get_json_body,
    URLLIB3_REQUEST, patch
)

MOCK_RESPONSE = api_response_mock()

# External IDs for metadata fields and metadata_rules that should be created and later deleted
EXTERNAL_ID_ENUM = "metadata_external_id_enum_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_SET = "metadata_external_id_set_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_METADATA_RULE_GENERAL = "metadata_rule_id_general_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_METADATA_RULE_DELETE = "metadata_rule_id_deletion_{}".format(UNIQUE_TEST_ID)

# Sample datasource data
DATASOURCE_ENTRY_EXTERNAL_ID = "metadata_datasource_entry_external_id{}".format(UNIQUE_TEST_ID)

disable_warnings()

class MetadataRulesTest(unittest.TestCase):
    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_list_metadata_rules(self, mocker):
        """Test getting a list of all metadata rules"""

        mocker.return_value = MOCK_RESPONSE
        api.list_metadata_rules()

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "GET")


    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_create_metadata_rule(self, mocker):
        """Test creating an and metadata rule"""

        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_rule({
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "condition": { "metadata_field_id": EXTERNAL_ID_SET, "equals": DATASOURCE_ENTRY_EXTERNAL_ID },
            "result": { "enable": True, "activate_values": "all" },
            "name": EXTERNAL_ID_ENUM 
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "name": EXTERNAL_ID_ENUM,
            "condition": { "metadata_field_id": EXTERNAL_ID_SET, "equals": DATASOURCE_ENTRY_EXTERNAL_ID },
            "result": { "enable": True, "activate_values": "all" },
        })
    

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test03_create_and_metadata_rule(self, mocker):
        """Test creating an and metadata rule"""

        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_rule({
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "condition": {"and": [
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
            ]},
            "result": { "enable": True, "apply_value": {"value": "value1_and_value2","mode": "default"}},
            "name": EXTERNAL_ID_ENUM + "_AND" 
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "name": EXTERNAL_ID_ENUM + "_AND" ,
            "condition": {"and": [
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
            ]},
            "result": { "enable": True, "apply_value": {"value": "value1_and_value2","mode": "default"}},
        })


    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test04_create_or_metadata_rule(self,mocker):
        """Test creating an or metadata rule"""

        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_rule({
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "condition": {"or": [
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
            ]},
            "result": { "enable": True, "apply_value": {"value": "value1_or_value2","mode": "default"}},
            "name": EXTERNAL_ID_ENUM + "_OR" 
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "name": EXTERNAL_ID_ENUM + "_OR",
            "condition": {"or": [
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
            ]},
            "result": { "enable": True, "apply_value": {"value": "value1_or_value2","mode": "default"}},
        })


    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_create_and_or_metadata_rule(self, mocker):
        """Test creating an and+or metadata rule"""

        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_rule({
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "condition": {"and": [
                { "metadata_field_id": EXTERNAL_ID_SET, "populated": True },
                {"or": [
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
                ]}
            ]},
            "result": { "enable": True, "activate_values": "all"},
            "name": EXTERNAL_ID_ENUM + "_AND_OR" 
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "name": EXTERNAL_ID_ENUM + "_AND_OR",
            "condition": {"and": [
                { "metadata_field_id": EXTERNAL_ID_SET, "populated": True },
                {"or": [
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
                ]}
            ]},
            "result": { "enable": True, "activate_values": "all"},
        })


    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_create_or_and_metadata_rule(self,mocker):
        """Test creating an or+and metadata rule"""

        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_rule({
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "condition": {"or": [
                {"metadata_field_id": EXTERNAL_ID_SET, "populated": False },
                {"and": [
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
                ]}
            ]},
            "result": { "enable": True, "activate_values": {"external_ids": ["value1","value2"]}},
            "name": EXTERNAL_ID_ENUM + "_OR_AND" 
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "name": EXTERNAL_ID_ENUM + "_OR_AND",
            "condition": {"or": [
                {"metadata_field_id": EXTERNAL_ID_SET, "populated": False },
                {"and": [
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": [DATASOURCE_ENTRY_EXTERNAL_ID]},
                    {"metadata_field_id": EXTERNAL_ID_SET,"includes": ["value2"]}
                ]}
            ]},
            "result": { "enable": True, "activate_values": {"external_ids": ["value1","value2"]}},
        })

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07_update_metadata_rule(self,mocker):
        """Update a metadata rule by external id"""
        mocker.return_value = MOCK_RESPONSE

        new_name = "update_metadata_rule_new_name{}".format(EXTERNAL_ID_METADATA_RULE_GENERAL)

        api.update_metadata_rule(EXTERNAL_ID_METADATA_RULE_GENERAL, {
            "metadata_field_id": EXTERNAL_ID_ENUM,
            "name": new_name + "_inactive",
            "condition": {},
            "result": {},
            "state": "inactive"
        })

        target_uri = "/metadata_rules/{}".format(EXTERNAL_ID_METADATA_RULE_GENERAL)
        self.assertTrue(get_uri(mocker).endswith(target_uri))
        self.assertEqual(get_method(mocker), "PUT")
        self.assertEqual(get_params(mocker).get("state"), "inactive")
        self.assertEqual(get_params(mocker).get("name"), new_name + "_inactive")

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08_delete_metadata_rule(self, mocker):
        """Test deleting a metadata rule definition by its external id."""

        mocker.return_value = MOCK_RESPONSE
        api.delete_metadata_rule(EXTERNAL_ID_METADATA_RULE_DELETE)

        target_uri = "/metadata_rules/{}".format(EXTERNAL_ID_METADATA_RULE_DELETE)
        self.assertTrue(get_uri(mocker).endswith(target_uri))
        self.assertEqual(get_method(mocker), "DELETE")

        self.assertEqual(get_json_body(mocker), {})


if __name__ == "__main__":
    unittest.main()
