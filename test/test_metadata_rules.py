import time
import unittest
from datetime import datetime, timedelta

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

METADATA_FIELDS = [
    EXTERNAL_ID_ENUM,
    EXTERNAL_ID_SET,
]
# Sample datasource data
DATASOURCE_ENTRY_EXTERNAL_ID = "metadata_datasource_entry_external_id{}".format(UNIQUE_TEST_ID)

# Sample datasource data
DATASOURCE_MULTIPLE = [
    {
        "value": "v2",
        "external_id": DATASOURCE_ENTRY_EXTERNAL_ID,
    },
    {
        "value": "v3",
    },
    {
        "value": "v4",
    },
]

# Sample metadata_field data
METADATA_FIELDS_TO_CREATE = [
    {
        "external_id": EXTERNAL_ID_ENUM,
        "type": "enum",
        "datasource": {
            "values": DATASOURCE_MULTIPLE,
        },
    },
    {
        "external_id": EXTERNAL_ID_SET,
        "type": "set",
        "datasource": {
            "values": DATASOURCE_MULTIPLE,
        },
    }
]

"""
METADATA_RULES_TO_CREATE = [
    {
        "metadata_field_id": ID_METADATA_RULE_DELETE,
        "name": ID_METADATA_RULE_DELETE,
        "condition": { "metadata_field_id": EXTERNAL_ID_SET, "equals": DATASOURCE_ENTRY_EXTERNAL_ID },
        "result": { "enable": True, "activate_values": "all" },
    },
    {
        "metadata_field_id": ID_METADATA_RULE_GENERAL,
        "name": ID_METADATA_RULE_GENERAL,
        "condition": { "metadata_field_id": EXTERNAL_ID_SET, "equals": DATASOURCE_ENTRY_EXTERNAL_ID },
        "result": { "enable": True, "activate_values": "all" },
    },
    
]
"""
disable_warnings()

class MetadataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        if not cloudinary.config().api_secret:
            return

        for field in METADATA_FIELDS_TO_CREATE:
            if "label" not in field:
                field["label"] = field["external_id"]

            api.add_metadata_field(field)
        
        """
        for rule in METADATA_RULES_TO_CREATE:
             api.add_metadata_rule(rule)
        """

    @classmethod
    def tearDownClass(cls):

        for external_id in METADATA_FIELDS:
            with ignore_exception(suppress_traceback_classes=(NotFound,)):
                api.delete_metadata_field(external_id)

    def assert_metadata_rule(self, metadata_rule, conditions=None, results=None):
        """Asserts that a given object fits the generic structure of a metadata field

        See: `Generic structure of a metadata field in API reference
        <https://cloudinary.com/documentation/admin_api#generic_structure_of_a_metadata_field>`_

        :param metadata_rule: The object to test
        :param conditions: An associative array where the key is the name of the parameter to check and the
               value is the condition
        :param results: An associative array where the key is the name of the parameter to check and the
               value is the results
        """
        self.assertIsInstance(metadata_rule["external_id"], text_type)
        self.assertIsInstance(metadata_rule["metadata_field_id"], text_type)

        self.assert_metadata_rule_condition(metadata_rule["condition"])
        self.assert_metadata_rule_result(metadata_rule["result"])

        self.assertIsInstance(condition, dict)
        self.assertIsInstance(result, dict)


    def assert_metadata_rule_condition(self, condition):
        """Asserts that a given object fits the generic structure of a metadata rule condition

        See: `Condition values in Admin API <https://cloudinary.com/documentation/admin_api#condition_structure>`_

        :param condition:
        """
        self.assertTrue(condition)
        self.assertIsInstance(condition["metadata_field_id"], text_type)
        if condition["includes"]:
          self.assertIsInstance(condition["includes"], dict)
        elif condition["populated"]:
          self.assertIsInstance(condition["populated"], bool)
        elif condition["equals"]:
          self.assertIsInstance(condition["equals"], text_type)
        elif condition["or"]:
          self.assertIsInstance(condition["or"], dict)
        elif condition["and"]:
          self.assertIsInstance(condition["and"], dict)


    def assert_metadata_rule_result(self, result):
        """Asserts that a given object fits the generic structure of a metadata rule result

        See: `Result result in Admin API <https://cloudinary.com/documentation/admin_api#result_structure>`_

        :param result:
        """
        self.assertTrue(result)
        self.assertIsInstance(result["enable"], bool)
        if result["activate_values"]:
          self.assertIsInstance(result["activate_values"], dict)
        elif result["apply_value"]:
          self.assertIsInstance(result["apply_value"], dict)
        elif result["set_mandatory"]:
          self.assertIsInstance(result["set_mandatory"], bool)


    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_list_metadata_rules(self, mocker):
        """Test getting a list of all metadata rules"""

        mocker.return_value = MOCK_RESPONSE
        api.list_metadata_rules()

        self.assertTrue(get_uri(mocker).endswith("/metadata_rules"))
        self.assertEqual(get_method(mocker), "GET")
        self.assertFalse(get_params(mocker).get("metadata_rules"))


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

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07_update_metadata_rule(self):
        """Update a metadata rule by external id"""

        new_name = "update_metadata_rule_new_name{}".format(ID_METADATA_RULE_GENERAL)

        result = api.update_metadata_rule(EXTERNAL_ID_METADATA_RULE_GENERAL, {
            "name": new_name + "_inactive",
            "state": "inactive"
        })

        self.assert_metadata_rule(result, "string", {
            "external_id": EXTERNAL_ID_METADATA_RULE_GENERAL,
            "name": new_name + "_inactive",
            "state": "inactive"
        })


    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test8_delete_metadata_rule(self, mocker):
        """Test deleting a metadata rule definition by its external id."""

        mocker.return_value = MOCK_RESPONSE
        api.delete_metadata_rule(EXTERNAL_ID_METADATA_RULE_DELETE)

        target_uri = "/metadata_rules/{}".format(EXTERNAL_ID_METADATA_RULE_DELETE)
        self.assertTrue(get_uri(mocker).endswith(target_uri))
        self.assertEqual(get_method(mocker), "DELETE")

        self.assertEqual(get_json_body(mocker), {})


if __name__ == "__main__":
    unittest.main()
