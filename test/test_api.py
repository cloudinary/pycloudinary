import time
import unittest
from collections import OrderedDict

import six
from mock import patch
from urllib3 import disable_warnings

import cloudinary
from cloudinary import api, uploader, utils
from test.helper_test import SUFFIX, TEST_IMAGE, get_uri, get_params, get_list_param, get_param, TEST_DOC, get_method, \
    UNIQUE_TAG, api_response_mock, ignore_exception, cleanup_test_resources_by_tag, cleanup_test_transformation, \
    cleanup_test_resources

MOCK_RESPONSE = api_response_mock()

UNIQUE_API_TAG = 'api_{}'.format(UNIQUE_TAG)
API_TEST_TAG = "api_test_{}_tag".format(SUFFIX)
API_TEST_PREFIX = "api_test_{}".format(SUFFIX)
API_TEST_ID = "api_test_{}".format(SUFFIX)
API_TEST_ID2 = "api_test_{}2".format(SUFFIX)
API_TEST_ID3 = "api_test_{}3".format(SUFFIX)
API_TEST_ID4 = "api_test_{}4".format(SUFFIX)
API_TEST_ID5 = "api_test_{}5".format(SUFFIX)
API_TEST_TRANS = "api_test_transformation_{}".format(SUFFIX)
API_TEST_TRANS2 = "api_test_transformation_{}2".format(SUFFIX)
API_TEST_TRANS3 = "api_test_transformation_{}3".format(SUFFIX)
API_TEST_TRANS_OVERLAY = {"font_family": "arial", "font_size": 20, "text": SUFFIX}
API_TEST_TRANS_OVERLAY_STR = "text:arial_20:{}".format(SUFFIX)
API_TEST_TRANS_SCALE100 = {"crop": "scale", "width": 100, "overlay": API_TEST_TRANS_OVERLAY_STR}
API_TEST_TRANS_SCALE100_STR = "c_scale,l_{},w_100".format(API_TEST_TRANS_OVERLAY_STR)
API_TEST_TRANS_SEPIA = {"crop": "lfill", "width": 400, "effect": "sepia"}
API_TEST_TRANS_SEPIA_STR = "c_lfill,e_sepia,w_400"
API_TEST_PRESET = "api_test_upload_preset"
PREFIX = "test_folder_{}".format(SUFFIX)
MAPPING_TEST_ID = "api_test_upload_mapping_{}".format(SUFFIX)
RESTORE_TEST_ID = "api_test_restore_{}".format(SUFFIX)

disable_warnings()


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cloudinary.reset_config()
        if not cloudinary.config().api_secret:
            return
        print("Running tests for cloud: {}".format(cloudinary.config().cloud_name))
        for id in [API_TEST_ID, API_TEST_ID2]:
            uploader.upload(TEST_IMAGE,
                            public_id=id, tags=[API_TEST_TAG, ],
                            context="key=value", eager=[API_TEST_TRANS_SCALE100],
                            overwrite=True)

    @classmethod
    def tearDownClass(cls):
        cleanup_test_resources([([API_TEST_ID, API_TEST_ID2, API_TEST_ID3, API_TEST_ID4, API_TEST_ID5],)])

        cleanup_test_transformation([
            ([API_TEST_TRANS, API_TEST_TRANS2, API_TEST_TRANS3, API_TEST_TRANS_SCALE100_STR],),
        ])

        cleanup_test_resources_by_tag([
            (UNIQUE_API_TAG,),
            (UNIQUE_API_TAG, {'resource_type': 'raw'}),
        ])

        with ignore_exception(suppress_traceback_classes=(api.NotFound,)):
            api.delete_upload_mapping(MAPPING_TEST_ID)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_resource_types(self):
        """ should allow listing resource_types """
        self.assertIn("image", api.resource_types()["resource_types"])

    test01_resource_types.tags = ['safe']

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_resources(self, mocker):
        """ should allow listing resources """
        mocker.return_value = MOCK_RESPONSE
        api.resources()
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image'))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test03_resources_cursor(self):
        """ should allow listing resources with cursor """
        result = api.resources(max_results=1)
        self.assertNotEqual(result["resources"], None)
        self.assertEqual(len(result["resources"]), 1)
        self.assertNotEqual(result["next_cursor"], None)

        result2 = api.resources(max_results=1, next_cursor=result["next_cursor"])
        self.assertNotEqual(result2["resources"], None)
        self.assertEqual(len(result2["resources"]), 1)
        self.assertNotEqual(result2["resources"][0]["public_id"], result["resources"][0]["public_id"])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test04_resources_types(self, mocker):
        """ should allow listing resources by type """
        mocker.return_value = MOCK_RESPONSE
        api.resources(type="upload", context=True, tags=True)
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image/upload'))
        self.assertTrue(get_params(args)['context'])
        self.assertTrue(get_params(args)['tags'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_resources_prefix(self, mocker):
        """ should allow listing resources by prefix """
        mocker.return_value = MOCK_RESPONSE
        api.resources(prefix=API_TEST_PREFIX, context=True, tags=True, type="upload")
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image/upload'))
        self.assertEqual(get_params(args)['prefix'], API_TEST_PREFIX)
        self.assertTrue(get_params(args)['context'])
        self.assertTrue(get_params(args)['tags'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_resources_tag(self, mocker):
        """ should allow listing resources by tag """
        mocker.return_value = MOCK_RESPONSE
        api.resources_by_tag(API_TEST_TAG, context=True, tags=True)
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image/tags/{}'.format(API_TEST_TAG)))
        self.assertTrue(get_params(args)['context'])
        self.assertTrue(get_params(args)['tags'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06a_resources_by_ids(self, mocker):
        """ should allow listing resources by public ids """
        mocker.return_value = MOCK_RESPONSE
        api.resources_by_ids([API_TEST_ID, API_TEST_ID2], context=True, tags=True)
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image/upload'), get_uri(args))
        self.assertIn(API_TEST_ID, get_list_param(mocker, 'public_ids'))
        self.assertIn(API_TEST_ID2, get_list_param(mocker, 'public_ids'))
        self.assertEqual(get_param(mocker, 'context'), True)
        self.assertEqual(get_param(mocker, 'tags'), True)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06b_resources_direction(self, mocker):
        """ should allow listing resources in both directions """
        mocker.return_value = MOCK_RESPONSE
        api.resources_by_tag(API_TEST_TAG, direction="asc", type="upload")
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image/tags/{}'.format(API_TEST_TAG)))
        self.assertEqual(get_params(args)['direction'], 'asc')
        api.resources_by_tag(API_TEST_TAG, direction="desc", type="upload")
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/resources/image/tags/{}'.format(API_TEST_TAG)))
        self.assertEqual(get_params(args)['direction'], 'desc')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07_resource_metadata(self):
        """ should allow get resource metadata """
        resource = api.resource(API_TEST_ID)
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["public_id"], API_TEST_ID)
        self.assertEqual(resource["bytes"], 3381)
        self.assertEqual(len(resource["derived"]), 1, "{} should have one derived resource.".format(API_TEST_ID))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07a_resource_quality_analysis(self):
        """ should allow getting resource quality analysis """
        resource = api.resource(API_TEST_ID, quality_analysis=True)
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["public_id"], API_TEST_ID)
        self.assertIn("quality_analysis", resource)
        self.assertIn("focus", resource["quality_analysis"])
        self.assertIsInstance(resource["quality_analysis"]["focus"], float)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07b_resource_allows_derived_next_cursor_parameter(self, mocker):
        """ should allow derived_next_cursor parameter """
        mocker.return_value = MOCK_RESPONSE
        api.resource(API_TEST_ID, derived_next_cursor="foo")
        args, kwargs = mocker.call_args
        self.assertTrue("derived_next_cursor" in get_params(args))
    
    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08_delete_derived(self, mocker):
        """ should allow deleting derived resource """
        mocker.return_value = MOCK_RESPONSE
        api.delete_derived_resources([API_TEST_ID])
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/derived_resources'))
        self.assertIn(API_TEST_ID, get_list_param(mocker, 'derived_resource_ids'))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08a_delete_derived_by_transformation(self, mocker):
        """ should allow deleting derived resource by transformations """
        public_resource_id = 'public_resource_id'
        public_resource_id2 = 'public_resource_id2'
        transformation = {"crop": "scale", "width": 100}
        transformation2 = {"crop": "scale", "width": 200}

        mocker.return_value = MOCK_RESPONSE
        api.delete_derived_by_transformation(public_resource_id, transformation)
        method, url, params = mocker.call_args[0][0:3]
        self.assertEqual('DELETE', method)
        self.assertTrue(url.endswith('/resources/image/upload'))
        self.assertIn(public_resource_id, get_list_param(mocker, 'public_ids'))
        self.assertEqual(get_param(mocker, 'transformations'), utils.build_eager([transformation]))
        self.assertTrue(get_param(mocker, 'keep_original'))

        mocker.return_value = MOCK_RESPONSE
        api.delete_derived_by_transformation(
            [public_resource_id, public_resource_id2], [transformation, transformation2],
            resource_type='raw', type='fetch', invalidate=True, foo='bar')
        method, url, params = mocker.call_args[0][0:3]
        self.assertEqual('DELETE', method)
        self.assertTrue(url.endswith('/resources/raw/fetch'))
        self.assertIn(public_resource_id, get_list_param(mocker, 'public_ids'))
        self.assertIn(public_resource_id2, get_list_param(mocker, 'public_ids'))
        self.assertEqual(get_param(mocker, 'transformations'), utils.build_eager([transformation, transformation2]))
        self.assertTrue(get_param(mocker, 'keep_original'))
        self.assertTrue(get_param(mocker, 'invalidate'))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09_delete_resources(self, mocker):
        """ should allow deleting resources """
        mocker.return_value = MOCK_RESPONSE
        api.delete_resources([API_TEST_ID, API_TEST_ID2])
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'DELETE')
        self.assertTrue(get_uri(args).endswith('/resources/image/upload'))
        param = get_list_param(mocker, 'public_ids')
        self.assertIn(API_TEST_ID, param)
        self.assertIn(API_TEST_ID2, param)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09a_delete_resources_by_prefix(self, mocker):
        """ should allow deleting resources by prefix """
        mocker.return_value = MOCK_RESPONSE
        api.delete_resources_by_prefix("api_test")
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'DELETE')
        self.assertTrue(get_uri(args).endswith('/resources/image/upload'))
        self.assertEqual(get_params(args)['prefix'], "api_test")

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09b_delete_resources_by_tag(self, mocker):
        """ should allow deleting resources by tags """
        mocker.return_value = MOCK_RESPONSE
        api.delete_resources_by_tag("api_test_tag_for_delete")
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'DELETE')
        self.assertTrue(get_uri(args).endswith('/resources/image/tags/api_test_tag_for_delete'))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09c_delete_resources_by_transformations(self, mocker):
        """ should allow deleting resources by transformations """
        mocker.return_value = MOCK_RESPONSE

        api.delete_resources(['api_test', 'api_test2'], transformations=['c_crop,w_100'])
        self.assertEqual(get_method(mocker), 'DELETE')
        self.assertEqual(get_param(mocker, 'transformations'), 'c_crop,w_100')

        api.delete_all_resources(transformations=['c_crop,w_100', {"crop": "scale", "width": 107}])
        self.assertEqual(get_method(mocker), 'DELETE')
        self.assertEqual(get_param(mocker, 'transformations'), 'c_crop,w_100|c_scale,w_107')

        api.delete_resources_by_prefix("api_test_by", transformations='c_crop,w_100')
        self.assertEqual(get_method(mocker), 'DELETE')
        self.assertEqual(get_param(mocker, 'transformations'), 'c_crop,w_100')

        api.delete_resources_by_tag("api_test_tag", transformations=['c_crop,w_100'])
        self.assertEqual(get_method(mocker), 'DELETE')
        self.assertEqual(get_param(mocker, 'transformations'), 'c_crop,w_100')

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09_delete_resources_tuple(self, mocker):
        """ should allow deleting resources """
        mocker.return_value = MOCK_RESPONSE
        api.delete_resources((API_TEST_ID, API_TEST_ID2,))
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'DELETE')
        self.assertTrue(get_uri(args).endswith('/resources/image/upload'))
        param = get_list_param(mocker, 'public_ids')
        self.assertIn(API_TEST_ID, param)
        self.assertIn(API_TEST_ID2, param)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test10_tags(self, mocker):
        """ should allow listing tags """
        mocker.return_value = MOCK_RESPONSE
        api.tags()
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/tags/image'))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test11_tags_prefix(self, mocker):
        """ should allow listing tag by prefix """
        mocker.return_value = MOCK_RESPONSE
        api.tags(prefix=API_TEST_PREFIX)
        args, kargs = mocker.call_args
        self.assertTrue(get_uri(args).endswith('/tags/image'))
        self.assertEqual(get_params(args)['prefix'], API_TEST_PREFIX)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test12_transformations(self):
        """ should allow listing transformations """
        transformations = api.transformations()["transformations"]
        self.assertLess(0, len(transformations))
        transformation = transformations[0]
        self.assertIsNotNone(transformation)
        self.assertIn("used", transformation)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test12a_transformations_cursor(self, mocker):
        """ should allow listing transformations with cursor """
        mocker.return_value = MOCK_RESPONSE
        api.transformation(API_TEST_TRANS_SCALE100, next_cursor='2412515', max_results=10)
        params = mocker.call_args[0][2]
        self.assertEqual(params['next_cursor'], '2412515')
        self.assertEqual(params['max_results'], 10)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_transformations_list_named(self, mocker):
        """ should allow listing only named transformations"""
        mocker.return_value = MOCK_RESPONSE
        api.transformations(named=True)
        params = mocker.call_args[0][2]
        self.assertEqual(params['named'], True)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test13_transformation_metadata(self):
        """ should allow getting transformation metadata """
        transformation = api.transformation(API_TEST_TRANS_SCALE100_STR)
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["info"], [API_TEST_TRANS_SCALE100])
        transformation = api.transformation(API_TEST_TRANS_SCALE100)
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["info"], [API_TEST_TRANS_SCALE100])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test14_transformation_update(self, mocker):
        """ should allow updating transformation allowed_for_strict """
        mocker.return_value = MOCK_RESPONSE
        api.update_transformation(API_TEST_TRANS_SCALE100_STR, allowed_for_strict=True)
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'PUT')
        self.assertTrue(get_uri(args).endswith('/transformations'))
        self.assertTrue(get_params(args)['allowed_for_strict'])
        self.assertEqual(API_TEST_TRANS_SCALE100_STR, get_params(args)['transformation'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15_transformation_create(self, mocker):
        """ should allow creating named transformation """
        mocker.return_value = MOCK_RESPONSE
        api.create_transformation(API_TEST_TRANS, {"crop": "scale", "width": 102})
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'POST')
        self.assertTrue(get_uri(args).endswith('/transformations'), get_uri(args))
        self.assertEqual(get_params(args)['transformation'], 'c_scale,w_102')
        self.assertEqual(API_TEST_TRANS, get_params(args)['name'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15a_transformation_unsafe_update(self):
        """ should allow unsafe update of named transformation """
        api.create_transformation(API_TEST_TRANS3, {"crop": "scale", "width": 102})
        api.update_transformation(API_TEST_TRANS3, unsafe_update={"crop": "scale", "width": 103})
        transformation = api.transformation(API_TEST_TRANS3)
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["info"], [{"crop": "scale", "width": 103}])
        self.assertEqual(transformation["used"], False)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15b_transformation_create_unnamed_with_format(self, mocker):
        """ should allow creating unnamed transformation with extension"""
        mocker.return_value = MOCK_RESPONSE

        with_extension = dict(API_TEST_TRANS_SCALE100)
        with_extension.update(format="jpg")

        with_extension_str = API_TEST_TRANS_SCALE100_STR + "/jpg"

        api.create_transformation(with_extension_str, with_extension)

        args, kargs = mocker.call_args

        self.assertEqual(args[0], 'POST')
        self.assertTrue(get_uri(args).endswith('/transformations'), get_uri(args))
        self.assertEqual(with_extension_str, get_params(args)['transformation'])
        self.assertEqual(with_extension_str, get_params(args)['name'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15c_transformation_create_unnamed_with_empty_format(self, mocker):
        """ should allow creating unnamed transformation with empty extension"""
        mocker.return_value = MOCK_RESPONSE

        with_extension = dict(API_TEST_TRANS_SCALE100)
        with_extension.update(format="")

        with_extension_str = API_TEST_TRANS_SCALE100_STR + "/"

        api.create_transformation(with_extension_str, with_extension)

        args, kargs = mocker.call_args

        self.assertEqual(args[0], 'POST')
        self.assertTrue(get_uri(args).endswith('/transformations'), get_uri(args))
        self.assertEqual(with_extension_str, get_params(args)['transformation'])
        self.assertEqual(with_extension_str, get_params(args)['name'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test16_transformation_delete(self):
        """ should allow deleting named transformation """
        api.create_transformation(API_TEST_TRANS2, {"crop": "scale", "width": 103})
        api.transformation(API_TEST_TRANS2)
        api.delete_transformation(API_TEST_TRANS2)
        self.assertRaises(api.NotFound, api.transformation, API_TEST_TRANS2)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test17_transformation_implicit(self, mocker):
        """ should allow deleting implicit transformation """
        mocker.return_value = MOCK_RESPONSE
        api.delete_transformation(API_TEST_TRANS_SCALE100)
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'DELETE')
        self.assertTrue(get_uri(args).endswith('/transformations'))
        self.assertEqual(API_TEST_TRANS_SCALE100_STR, get_params(args)['transformation'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test18_usage(self):
        """ should support usage API """
        self.assertIn("last_updated", api.usage())

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skip("Skip delete all derived resources by default")
    def test19_delete_derived(self):
        """ should allow deleting all resource """
        uploader.upload(TEST_IMAGE, public_id=API_TEST_ID5, eager=[{"width": 101, "crop": "scale"}])
        resource = api.resource(API_TEST_ID5)
        self.assertNotEqual(resource, None)
        self.assertEqual(len(resource["derived"]), 1)
        api.delete_all_resources(keep_original=True)
        resource = api.resource(API_TEST_ID5)
        self.assertNotEqual(resource, None)
        self.assertEqual(len(resource["derived"]), 0)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test20_manual_moderation(self):
        """ should support setting manual moderation status """
        resource = uploader.upload(TEST_IMAGE, moderation="manual", tags=[UNIQUE_API_TAG])

        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")

        api_result = api.update(resource["public_id"], moderation_status="approved")
        self.assertEqual(api_result["moderation"][0]["status"], "approved")
        self.assertEqual(api_result["moderation"][0]["kind"], "manual")

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test21_notification_url(self, mocker):
        """ should support notification_url param """
        mocker.return_value = MOCK_RESPONSE
        api.update("api_test", notification_url="http://example.com")
        params = mocker.call_args[0][2]
        self.assertEqual(params['notification_url'], "http://example.com")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test22_raw_conversion(self):
        """ should support requesting raw_convert """
        resource = uploader.upload(TEST_DOC, resource_type="raw", tags=[UNIQUE_API_TAG])
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update(resource["public_id"], raw_convert="illegal", resource_type="raw")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test23_categorization(self):
        """ should support requesting categorization """
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update(API_TEST_ID, categorization="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test24_detection(self):
        """ should support requesting detection """
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update(API_TEST_ID, detection="illegal")

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test26_1_ocr(self, mocker):
        """ should support requesting ocr """
        mocker.return_value = MOCK_RESPONSE
        api.update(API_TEST_ID, ocr='adv_ocr')
        args, kargs = mocker.call_args
        params = get_params(args)
        self.assertEqual(params['ocr'], 'adv_ocr')

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test26_2_quality_override(self, mocker):
        """ should support quality_override """
        mocker.return_value = MOCK_RESPONSE
        test_values = ['auto:advanced', 'auto:best', '80:420', 'none']
        for quality in test_values:
            api.update("api_test", quality_override=quality)
            params = mocker.call_args[0][2]
            self.assertEqual(params['quality_override'], quality)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test27_start_at(self, mocker):
        """ should allow listing resources by start date """
        mocker.return_value = MOCK_RESPONSE
        start_at = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        api.resources(type="upload", start_at=start_at, direction="asc")
        args, kargs = mocker.call_args
        params = get_params(args)
        self.assertEqual(params['start_at'], start_at)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test28_create_upload_preset(self, mocker):
        """ should allow creating upload_presets """
        mocker.return_value = MOCK_RESPONSE

        api.create_upload_preset(name=API_TEST_PRESET, folder="folder")

        args, kargs = mocker.call_args

        self.assertTrue(get_uri(args).endswith("/upload_presets"))
        self.assertEqual("POST", get_method(mocker))
        self.assertEqual(get_param(mocker, "name"), API_TEST_PRESET)
        self.assertEqual(get_param(mocker, "folder"), "folder")

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test28a_list_upload_presets(self, mocker):
        """ should allow listing upload_presets """
        mocker.return_value = MOCK_RESPONSE

        api.upload_presets()

        args, kargs = mocker.call_args

        self.assertTrue(get_uri(args).endswith("/upload_presets"))
        self.assertEqual("GET", get_method(mocker))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test29_get_upload_presets(self, mocker):
        """ should allow getting a single upload_preset """
        mocker.return_value = MOCK_RESPONSE

        api.upload_preset(API_TEST_PRESET)

        args, kargs = mocker.call_args

        self.assertTrue(get_uri(args).endswith("/upload_presets/" + API_TEST_PRESET))
        self.assertEqual("GET", get_method(mocker))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test30_delete_upload_presets(self, mocker):
        """ should allow deleting upload_presets """
        mocker.return_value = MOCK_RESPONSE
        api.delete_upload_preset(API_TEST_PRESET)
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'DELETE')
        self.assertTrue(get_uri(args).endswith('/upload_presets/{}'.format(API_TEST_PRESET)))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test31_update_upload_presets(self, mocker):
        """ should allow getting a single upload_preset """
        mocker.return_value = MOCK_RESPONSE
        api.update_upload_preset(API_TEST_PRESET, colors=True, unsigned=True, disallow_public_id=True)
        args, kargs = mocker.call_args
        self.assertEqual(args[0], 'PUT')
        self.assertTrue(get_uri(args).endswith('/upload_presets/{}'.format(API_TEST_PRESET)))
        self.assertTrue(get_params(args)['colors'])
        self.assertTrue(get_params(args)['unsigned'])
        self.assertTrue(get_params(args)['disallow_public_id'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test32_background_removal(self):
        """ should support requesting background_removal """
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update(API_TEST_ID, background_removal="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skip("For this test to work, 'Auto-create folders' should be enabled in the Upload Settings, " +
                   "and the account should be empty of folders. " +
                   "Comment out this line if you really want to test it.")
    def test_folder_listing(self):
        """ should support listing folders """
        uploader.upload(TEST_IMAGE, public_id="{}1/item".format(PREFIX), tags=[UNIQUE_API_TAG])
        uploader.upload(TEST_IMAGE, public_id="{}2/item".format(PREFIX), tags=[UNIQUE_API_TAG])
        uploader.upload(TEST_IMAGE, public_id="{}1/test_subfolder1/item".format(PREFIX), tags=[UNIQUE_API_TAG])
        uploader.upload(TEST_IMAGE, public_id="{}1/test_subfolder2/item".format(PREFIX), tags=[UNIQUE_API_TAG])
        result = api.root_folders()
        self.assertEqual(result["folders"][0]["name"], "{}1".format(PREFIX))
        self.assertEqual(result["folders"][1]["name"], "{}2".format(PREFIX))
        result = api.subfolders("{}1".format(PREFIX))
        self.assertEqual(result["folders"][0]["path"], "{}1/test_subfolder1".format(PREFIX))
        self.assertEqual(result["folders"][1]["path"], "{}1/test_subfolder2".format(PREFIX))
        with six.assertRaisesRegex(self, api.NotFound):
            api.subfolders(PREFIX)

    def test_CloudinaryImage_len(self):
        """Tests the __len__ function on CloudinaryImage"""
        metadata = {
            "public_id": "test_id",
            "format": "tst",
            "version": "1234",
            "signature": "5678",
        }
        my_cloudinary_image = cloudinary.CloudinaryImage(metadata=metadata)
        self.assertEqual(len(my_cloudinary_image), len(metadata["public_id"]))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_restore(self):
        """ should support restoring resources """
        uploader.upload(TEST_IMAGE, public_id=RESTORE_TEST_ID, backup=True, tags=[UNIQUE_API_TAG])
        resource = api.resource(RESTORE_TEST_ID)
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["bytes"], 3381)
        api.delete_resources([RESTORE_TEST_ID])
        resource = api.resource(RESTORE_TEST_ID)
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["bytes"], 0)
        self.assertIs(resource["placeholder"], True)
        response = api.restore([RESTORE_TEST_ID])
        info = response[RESTORE_TEST_ID]
        self.assertNotEqual(info, None)
        self.assertEqual(info["bytes"], 3381)
        resource = api.resource(RESTORE_TEST_ID)
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["bytes"], 3381)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_mapping(self):

        api.create_upload_mapping(MAPPING_TEST_ID, template="http://cloudinary.com", tags=[UNIQUE_API_TAG])
        result = api.upload_mapping(MAPPING_TEST_ID)
        self.assertEqual(result["template"], "http://cloudinary.com")
        api.update_upload_mapping(MAPPING_TEST_ID, template="http://res.cloudinary.com")
        result = api.upload_mapping(MAPPING_TEST_ID)
        self.assertEqual(result["template"], "http://res.cloudinary.com")
        result = api.upload_mappings()
        self.assertIn({"folder": MAPPING_TEST_ID, "template": "http://res.cloudinary.com"},
                      result["mappings"])
        api.delete_upload_mapping(MAPPING_TEST_ID)
        result = api.upload_mappings()
        self.assertNotIn(MAPPING_TEST_ID, [mapping.get("folder") for mapping in result["mappings"]])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_publish_by_ids(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        api.publish_by_ids(["pub1", "pub2"])
        self.assertTrue(get_uri(mocker.call_args[0]).endswith('/resources/image/publish_resources'))
        self.assertIn('pub1', get_list_param(mocker, 'public_ids'))
        self.assertIn('pub2', get_list_param(mocker, 'public_ids'))

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_publish_by_prefix(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        api.publish_by_prefix("pub_prefix")
        self.assertTrue(get_uri(mocker.call_args[0]).endswith('/resources/image/publish_resources'))
        self.assertEqual(get_param(mocker, 'prefix'), 'pub_prefix')

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_publish_by_tag(self, mocker):
        mocker.return_value = MOCK_RESPONSE
        api.publish_by_tag("pub_tag")
        self.assertTrue(get_uri(mocker.call_args[0]).endswith('/resources/image/publish_resources'))
        self.assertEqual(get_param(mocker, 'tag'), "pub_tag")

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_update_access_control(self, mocker):
        """ should allow the user to define ACL in the update parameters """
        mocker.return_value = MOCK_RESPONSE

        acl = OrderedDict((("access_type", "anonymous"),
                           ("start", "2018-02-22 16:20:57 +0200"),
                           ("end", "2018-03-22 00:00 +0200")))
        exp_acl = '[{"access_type":"anonymous","start":"2018-02-22 16:20:57 +0200","end":"2018-03-22 00:00 +0200"}]'

        api.update(API_TEST_ID, access_control=acl)

        params = get_params(mocker.call_args[0])

        self.assertIn("access_control", params)
        self.assertEqual(exp_acl, params["access_control"])


if __name__ == '__main__':
    unittest.main()
