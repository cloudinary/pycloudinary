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

# External IDs for metadata fields that should be created and later deleted
EXTERNAL_ID_GENERAL = "metadata_external_id_general_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_DATE = "metadata_external_id_date_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_ENUM_2 = "metadata_external_id_enum_2_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_SET = "metadata_external_id_set_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_SET_2 = "metadata_external_id_set_2_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_SET_3 = "metadata_external_id_set_3_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_DELETE_2 = "metadata_deletion_2_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_DATE_VALIDATION = "metadata_date_validation_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_DATE_VALIDATION_2 = "metadata_date_validation_2_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_INT_VALIDATION = "metadata_int_validation_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_INT_VALIDATION_2 = "metadata_int_validation_2_{}".format(UNIQUE_TEST_ID)

METADATA_FIELDS = [
    EXTERNAL_ID_GENERAL,
    EXTERNAL_ID_DATE,
    EXTERNAL_ID_ENUM_2,
    EXTERNAL_ID_SET,
    EXTERNAL_ID_SET_2,
    EXTERNAL_ID_SET_3,
    EXTERNAL_ID_DELETE_2,
    EXTERNAL_ID_DATE_VALIDATION,
    EXTERNAL_ID_DATE_VALIDATION_2,
    EXTERNAL_ID_INT_VALIDATION,
    EXTERNAL_ID_INT_VALIDATION_2,
]

# External IDs for metadata fields that will be accessed through a mock (and should not be deleted or created)
EXTERNAL_ID_STRING = "metadata_external_id_string_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_INT = "metadata_external_id_int_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_ENUM = "metadata_external_id_enum_{}".format(UNIQUE_TEST_ID)
EXTERNAL_ID_DELETE = "metadata_deletion_{}".format(UNIQUE_TEST_ID)

# Sample datasource data
DATASOURCE_ENTRY_EXTERNAL_ID = "metadata_datasource_entry_external_id{}".format(UNIQUE_TEST_ID)

DATASOURCE_SINGLE = [
    {
        "value": "v1",
        "external_id": DATASOURCE_ENTRY_EXTERNAL_ID,
    },
]
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

METADATA_FIELDS_TO_CREATE = [
    {
        "external_id": EXTERNAL_ID_GENERAL,
        "type": "string",
    },
    {
        "external_id": EXTERNAL_ID_ENUM_2,
        "type": "enum",
        "datasource": {
            "values": DATASOURCE_MULTIPLE,
        },
    },
    {
        "external_id": EXTERNAL_ID_SET_2,
        "type": "set",
        "datasource": {
            "values": DATASOURCE_MULTIPLE,
        },
    },
    {
        "external_id": EXTERNAL_ID_SET_3,
        "type": "set",
        "datasource": {
            "values": DATASOURCE_MULTIPLE,
        },
    },
    {
        "external_id": EXTERNAL_ID_DELETE_2,
        "type": "integer",
    },
]

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

    @classmethod
    def tearDownClass(cls):
        for external_id in METADATA_FIELDS:
            with ignore_exception(suppress_traceback_classes=(NotFound,)):
                api.delete_metadata_field(external_id)

    def assert_metadata_field(self, metadata_field, field_type=None, values=None):
        """Asserts that a given object fits the generic structure of a metadata field

        See: `Generic structure of a metadata field in API reference
        <https://cloudinary.com/documentation/admin_api#generic_structure_of_a_metadata_field>`_

        :param metadata_field: The object to test
        :param field_type: The type of metadata field we expect
        :param values: An associative array where the key is the name of the parameter to check and the
               value is the value
        """
        self.assertIsInstance(metadata_field["external_id"], text_type)

        if field_type:
            self.assertEqual(metadata_field["type"], field_type)
        else:
            self.assertIn(metadata_field["type"], ["string", "integer", "date", "enum", "set"])

        self.assertIsInstance(metadata_field["label"], text_type)
        self.assertIsInstance(metadata_field["mandatory"], bool)

        self.assertIn("default_value", metadata_field)
        self.assertIn("validation", metadata_field)

        if metadata_field["type"] in ["enum", "set"]:
            self.assert_metadata_field_datasource(metadata_field["datasource"])

        values = values or {}
        for key, value in values.items():
            self.assertEqual(metadata_field[key], value)

    def assert_metadata_field_datasource(self, datasource):
        """Asserts that a given object fits the generic structure of a metadata field datasource

        See: `Datasource values in Admin API <https://cloudinary.com/documentation/admin_api#datasource_values>`_

        :param datasource:
        """
        self.assertTrue(datasource)
        self.assertIn("values", datasource)

        if datasource["values"]:
            self.assertIsInstance(datasource["values"][0]["value"], text_type)
            self.assertIsInstance(datasource["values"][0]["external_id"], text_type)
            if "state" in datasource["values"][0]:
                self.assertIn(datasource["values"][0]["state"], ["active", "inactive"])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_list_metadata_fields(self, mocker):
        """Test getting a list of all metadata fields"""
        mocker.return_value = MOCK_RESPONSE
        api.list_metadata_fields()

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields"))
        self.assertEqual(get_method(mocker), "GET")
        self.assertFalse(get_params(mocker).get("fields"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_get_metadata_field(self):
        """Test getting a metadata field by external id"""
        result = api.metadata_field_by_field_id(EXTERNAL_ID_GENERAL)

        self.assert_metadata_field(result, "string", {"label": EXTERNAL_ID_GENERAL})

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test03_create_string_metadata_field(self, mocker):
        """Test creating a string metadata field"""
        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_field({
            "external_id": EXTERNAL_ID_STRING,
            "label": EXTERNAL_ID_STRING,
            "type": "string",
            "restrictions": {"readonly_ui": True},
            "mandatory": False,
            "default_disabled": True
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            'default_disabled': True,
            "type": "string",
            "external_id": EXTERNAL_ID_STRING,
            "label": EXTERNAL_ID_STRING,
            'mandatory': False,
            "restrictions": {"readonly_ui": True}
        })

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test04_create_int_metadata_field(self, mocker):
        """Test creating an integer metadata field"""
        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_field({
            "external_id": EXTERNAL_ID_INT,
            "label": EXTERNAL_ID_INT,
            "type": "integer",
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "type": "integer",
            "external_id": EXTERNAL_ID_INT,
            "label": EXTERNAL_ID_INT,
        })

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_create_date_metadata_field(self):
        """Test creating a date metadata field"""
        result = api.add_metadata_field({
            "external_id": EXTERNAL_ID_DATE,
            "label": EXTERNAL_ID_DATE,
            "type": "date",
            "restrictions": {"readonly_ui": True}
        })

        self.assert_metadata_field(result, "date", {
            "label": EXTERNAL_ID_DATE,
            "external_id": EXTERNAL_ID_DATE,
            "mandatory": False,
            "restrictions": {"readonly_ui": True}
        })

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_create_enum_metadata_field(self, mocker):
        """Test creating an Enum metadata field"""
        mocker.return_value = MOCK_RESPONSE
        api.add_metadata_field({
            "datasource": {
                "values": DATASOURCE_SINGLE,
            },
            "external_id": EXTERNAL_ID_ENUM,
            "label": EXTERNAL_ID_ENUM,
            "type": "enum",
        })

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields"))
        self.assertEqual(get_method(mocker), "POST")
        self.assertEqual(get_json_body(mocker), {
            "datasource": {
                "values": DATASOURCE_SINGLE,
            },
            "external_id": EXTERNAL_ID_ENUM,
            "label": EXTERNAL_ID_ENUM,
            "type": "enum",
        })

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07_create_set_metadata_field(self):
        """Test creating a set metadata field"""
        result = api.add_metadata_field({
            "datasource": {
                "values": DATASOURCE_MULTIPLE,
            },
            "external_id": EXTERNAL_ID_SET,
            "label": EXTERNAL_ID_SET,
            "type": "set",
            "allow_dynamic_list_values": True,
        })

        self.assert_metadata_field(result, "set", {
            "label": EXTERNAL_ID_SET,
            "external_id": EXTERNAL_ID_SET,
            "mandatory": False,
            "allow_dynamic_list_values": True,
        })

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08_update_metadata_field(self):
        """Update a metadata field by external id"""
        new_label = "update_metadata_test_new_label{}".format(EXTERNAL_ID_GENERAL)
        new_default_value = "update_metadata_test_new_default_value{}".format(EXTERNAL_ID_GENERAL)

        # Call the API to update the metadata field
        # Will also attempt to update some fields that cannot be updated
        # (external_id and type) which will be ignored
        result = api.update_metadata_field(EXTERNAL_ID_GENERAL, {
            "external_id": EXTERNAL_ID_SET,
            "label": new_label,
            "type": "integer",
            "mandatory": True,
            "default_value": new_default_value,
            "restrictions": {"readonly_ui": True}
        })

        self.assert_metadata_field(result, "string", {
            "external_id": EXTERNAL_ID_GENERAL,
            "label": new_label,
            "default_value": new_default_value,
            "mandatory": True,
            "restrictions": {"readonly_ui": True}
        })

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09_update_metadata_field_datasource(self):
        """Update a metadata field datasource"""
        result = api.update_metadata_field_datasource(EXTERNAL_ID_ENUM_2, DATASOURCE_SINGLE)

        self.assert_metadata_field_datasource(result)

        matched = False
        for item in result["values"]:
            if item == DATASOURCE_SINGLE[0]:
                matched = True

        self.assertTrue(matched, msg="The updated metadata field does not contain the updated datasource")

        self.assertEqual(len(DATASOURCE_MULTIPLE), len(result["values"]))
        self.assertEqual(DATASOURCE_SINGLE[0]["value"], result["values"][0]["value"])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test10_delete_metadata_field(self, mocker):
        """Test deleting a metadata field definition by its external id."""
        mocker.return_value = MOCK_RESPONSE
        api.delete_metadata_field(EXTERNAL_ID_DELETE)

        target_uri = "/metadata_fields/{}".format(EXTERNAL_ID_DELETE)
        self.assertTrue(get_uri(mocker).endswith(target_uri))
        self.assertEqual(get_method(mocker), "DELETE")

        self.assertEqual(get_json_body(mocker), {})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test12_delete_metadata_field_data_source(self):
        """Delete entries in a metadata field datasource"""
        result = api.delete_datasource_entries(EXTERNAL_ID_SET_2, [DATASOURCE_ENTRY_EXTERNAL_ID])

        self.assert_metadata_field_datasource(result)
        self.assertEqual(len(DATASOURCE_MULTIPLE) - 1, len(result["values"]))

        values = [item["value"] for item in result["values"]]

        self.assertIn(DATASOURCE_MULTIPLE[1]["value"], values)
        self.assertIn(DATASOURCE_MULTIPLE[2]["value"], values)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test13_date_field_default_value_validation(self):
        """Test date field validation"""
        today = datetime.now()
        past_date = today - timedelta(days=3)
        yesterday_date = today - timedelta(days=1)
        future_date = today + timedelta(days=3)
        last_three_days_validation = {
            "rules": [
                {
                    "type": "greater_than",
                    "equals": False,
                    "value": time.strftime("%Y-%m-%d", past_date.timetuple()),
                },
                {
                    "type": "less_than",
                    "equals": False,
                    "value": time.strftime("%Y-%m-%d", today.timetuple()),
                },
            ],
            "type": "and",
        }

        # Test entering a metadata field with date validation and a valid default value
        metadata_field = {
            "external_id": EXTERNAL_ID_DATE_VALIDATION,
            "label": EXTERNAL_ID_DATE_VALIDATION,
            "type": "date",
            "default_value": time.strftime("%Y-%m-%d", yesterday_date.timetuple()),
            "validation": last_three_days_validation,
        }
        result = api.add_metadata_field(metadata_field)

        self.assert_metadata_field(result, "date", {
            "validation": last_three_days_validation,
            "default_value": metadata_field["default_value"],
        })

        # Test entering a metadata field with date validation and an invalid default value
        with self.assertRaises(BadRequest):
            api.add_metadata_field({
                "external_id": EXTERNAL_ID_DATE_VALIDATION_2,
                "label": EXTERNAL_ID_DATE_VALIDATION_2,
                "type": "date",
                "default_value": time.strftime("%Y-%m-%d", future_date.timetuple()),
                "validation": last_three_days_validation,
            })

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test14_integer_field_validation(self):
        """Test integer field validation"""
        validation = {
            "type": "less_than",
            "equals": True,
            "value": 5,
        }

        # Test entering a metadata field with integer validation and a valid default value
        metadata_field = {
            "external_id": EXTERNAL_ID_INT_VALIDATION,
            "label": EXTERNAL_ID_INT_VALIDATION,
            "type": "integer",
            "default_value": 5,
            "validation": validation,
        }
        result = api.add_metadata_field(metadata_field)

        self.assert_metadata_field(result, "integer", {
            "validation": validation,
            "default_value": metadata_field["default_value"],
        })

        # Test entering a metadata field with integer validation and a valid default value
        with self.assertRaises(BadRequest):
            api.add_metadata_field({
                "external_id": EXTERNAL_ID_INT_VALIDATION_2,
                "label": EXTERNAL_ID_INT_VALIDATION_2,
                "type": "integer",
                "default_value": 6,
                "validation": validation,
            })

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15_restore_metadata_field_datasource(self):
        """Restore a deleted entry in a metadata field datasource"""
        # Begin by deleting a datasource entry
        result = api.delete_datasource_entries(EXTERNAL_ID_SET_3, [
            DATASOURCE_ENTRY_EXTERNAL_ID,
        ])

        self.assert_metadata_field_datasource(result)
        self.assertEqual(len(result["values"]), 2)

        # Restore datasource entry
        result = api.restore_metadata_field_datasource(EXTERNAL_ID_SET_3, [
            DATASOURCE_ENTRY_EXTERNAL_ID,
        ])

        self.assert_metadata_field_datasource(result)
        self.assertEqual(len(result["values"]), 3)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_order_by_asc_by_default_in_a_metadata_field_data_source(self):
        # datasource is set with values in the order v2, v3, v4
        result = api.reorder_metadata_field_datasource(EXTERNAL_ID_SET_3, 'value')

        self.assert_metadata_field_datasource(result)

        self.assertEqual(result['values'][0]['value'], DATASOURCE_MULTIPLE[0]['value'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_order_by_asc_in_a_metadata_field_data_source(self):
        # datasource is set with values in the order v2, v3, v4
        result = api.reorder_metadata_field_datasource(EXTERNAL_ID_SET_3, 'value', 'asc')

        self.assert_metadata_field_datasource(result)

        self.assertEqual(result['values'][0]['value'], DATASOURCE_MULTIPLE[0]['value'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_order_by_desc_in_a_metadata_field_data_source(self):
        # datasource is set with values in the order v2, v3, v4
        result = api.reorder_metadata_field_datasource(EXTERNAL_ID_SET_3, 'value', 'desc')

        self.assert_metadata_field_datasource(result)

        self.assertEqual(result['values'][0]['value'], DATASOURCE_MULTIPLE[-1]['value'])

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_reorder_metadata_fields_by_label(self, mocker):
        """Test the reorder of metadata fields for label order by asc"""
        mocker.return_value = MOCK_RESPONSE
        api.reorder_metadata_fields('label', 'asc')

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields/order"))
        self.assertEqual(get_method(mocker), "PUT")
        self.assertEqual(get_json_body(mocker)['order_by'], "label")
        self.assertEqual(get_json_body(mocker)['direction'], "asc")

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_reorder_metadata_fields_by_external_id(self, mocker):
        """Test the reorder of metadata fields for external_id order by desc"""
        mocker.return_value = MOCK_RESPONSE
        api.reorder_metadata_fields('external_id', 'desc')

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields/order"))
        self.assertEqual(get_method(mocker), "PUT")
        self.assertEqual(get_json_body(mocker)['order_by'], "external_id")
        self.assertEqual(get_json_body(mocker)['direction'], "desc")

    @patch(URLLIB3_REQUEST)
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_reorder_metadata_fields_by_created_at(self, mocker):
        """Test the reorder of metadata fields for created_at order by asc"""
        mocker.return_value = MOCK_RESPONSE
        api.reorder_metadata_fields('created_at', 'asc')

        self.assertTrue(get_uri(mocker).endswith("/metadata_fields/order"))
        self.assertEqual(get_method(mocker), "PUT")
        self.assertEqual(get_json_body(mocker)['order_by'], "created_at")
        self.assertEqual(get_json_body(mocker)['direction'], "asc")


if __name__ == "__main__":
    unittest.main()
