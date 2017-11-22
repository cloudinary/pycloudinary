import time
import unittest

from mock import patch
from urllib3._collections import HTTPHeaderDict

import cloudinary
import six
from cloudinary import uploader, api, utils

from urllib3 import disable_warnings, HTTPResponse


MOCK_HEADERS = HTTPHeaderDict({"x-featureratelimit-limit": '0', "x-featureratelimit-reset": 'Sat, 01 Apr 2017 22:00:00 GMT',
                          "x-featureratelimit-remaining": '0', })

if six.PY2:
    MOCK_RESPONSE = HTTPResponse(body='{"foo":"bar"}', headers=MOCK_HEADERS)
else:
    MOCK_RESPONSE = HTTPResponse(body='{"foo":"bar"}'.encode("UTF-8"), headers=MOCK_HEADERS)

disable_warnings()


class ApiTest(unittest.TestCase):
    initialized = False

    def setUp(self):
        self.timestamp_tag = "api_test_tag_{0}".format(utils.now())
        if ApiTest.initialized: return
        ApiTest.initialized = True
        cloudinary.reset_config()
        if not cloudinary.config().api_secret: return
        try:
            api.delete_resources(["api_test", "api_test2", "api_test3"])
        except Exception:
            pass
        for transformation in ["api_test_transformation", "api_test_transformation2", "api_test_transformation3"]:
            try:
                api.delete_transformation(transformation)
            except Exception:
                pass
        for transformation in ["api_test_upload_preset", "api_test_upload_preset2", "api_test_upload_preset3",
                               "api_test_upload_preset4"]:
            try:
                api.delete_upload_preset(transformation)
            except Exception:
                pass
        
        for id in ["api_test", "api_test2"]:
            uploader.upload("tests/logo.png",
                            public_id=id, tags=["api_test_tag", self.timestamp_tag],
                            context="key=value", eager=[{"width": 100, "crop": "scale"}])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_resource_types(self):
        """ should allow listing resource_types """
        self.assertIn("image", api.resource_types()["resource_types"])

    test01_resource_types.tags = ['safe']

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_resources(self):
        """ should allow listing resources """
        resource = [resource for resource in api.resources(max_results=500)["resources"] if resource["public_id"] == "api_test"][0]
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["type"], "upload")

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

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test04_resources_types(self):
        """ should allow listing resources by type """
        resources = api.resources(type="upload", max_results=500)["resources"]
        public_ids = [resource["public_id"] for resource in resources]
        self.assertIn("api_test", public_ids)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_resources_prefix(self):
        """ should allow listing resources by prefix """
        resources = api.resources(prefix="api_test", context=True, tags=True, type="upload", max_results=500)["resources"]
        public_ids = [resource["public_id"] for resource in resources]
        self.assertIn("api_test", public_ids)
        self.assertIn("api_test2", public_ids)
        resources_tags = [resource["tags"] for resource in resources]
        tags = [x for y in resources_tags for x in y]
        self.assertIn("api_test_tag", tags)
        self.assertIn({"custom": {"key": "value"}}, [resource.get("context") for resource in resources])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_resources_tag(self):
        """ should allow listing resources by tag """
        resources = api.resources_by_tag("api_test_tag", context=True, tags=True)["resources"]
        resource = [resource for resource in resources if resource["public_id"] == "api_test"][0]
        self.assertNotEqual(resource, None)
        resources_tags = [resource["tags"] for resource in resources]
        tags = [x for y in resources_tags for x in y]
        self.assertIn("api_test_tag", tags)
        self.assertIn({"custom": {"key": "value"}}, [resource.get("context") for resource in resources])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06a_resources_by_ids(self):
        """ should allow listing resources by public ids """
        resources = api.resources_by_ids(["api_test", "api_test2"], context=True, tags=True)["resources"]
        public_ids = [resource["public_id"] for resource in resources]
        self.assertEqual(sorted(public_ids), ["api_test", "api_test2"])
        resources_tags = [resource["tags"] for resource in resources]
        tags = [x for y in resources_tags for x in y]
        self.assertIn("api_test_tag", tags)
        self.assertIn({"custom": {"key": "value"}}, [resource.get("context") for resource in resources])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06b_resources_direction(self):
        """ should allow listing resources in both directions """
        asc_resources = api.resources_by_tag(self.timestamp_tag, direction="asc", type="upload")["resources"]
        desc_resources = api.resources_by_tag(self.timestamp_tag, direction="desc", type="upload")["resources"]
        asc_resources.reverse()
        self.assertEqual(asc_resources, desc_resources)
        asc_resources_alt = api.resources_by_tag(self.timestamp_tag, direction=1, type="upload")["resources"]
        desc_resources_alt = api.resources_by_tag(self.timestamp_tag, direction=-1, type="upload")["resources"]
        asc_resources_alt.reverse()
        self.assertEqual(asc_resources_alt, desc_resources_alt)
        self.assertEqual(asc_resources_alt, asc_resources)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test07_resource_metadata(self):
        """ should allow get resource metadata """
        resource = api.resource("api_test")
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["public_id"], "api_test")
        self.assertEqual(resource["bytes"], 3381)
        self.assertEqual(len(resource["derived"]), 1)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test08_delete_derived(self):
        """ should allow deleting derived resource """
        uploader.upload("tests/logo.png", public_id="api_test3", eager=[{"width": 101, "crop": "scale"}])
        resource = api.resource("api_test3")
        self.assertNotEqual(resource, None)
        self.assertEqual(len(resource["derived"]), 1)
        derived_resource_id = resource["derived"][0]["id"]
        api.delete_derived_resources([derived_resource_id])
        resource = api.resource("api_test3")
        self.assertNotEqual(resource, None)
        self.assertEqual(len(resource["derived"]), 0)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09_delete_resources(self):
        """ should allow deleting resources """
        uploader.upload("tests/logo.png", public_id="api_test3")
        resource = api.resource("api_test3")
        self.assertNotEqual(resource, None)
        api.delete_resources(["apit_test", "api_test2", "api_test3"])
        self.assertRaises(api.NotFound, api.resource, "api_test3")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09a_delete_resources_by_prefix(self):
        """ should allow deleting resources by prefix """
        uploader.upload("tests/logo.png", public_id="api_test_by_prefix")
        resource = api.resource("api_test_by_prefix")
        self.assertNotEqual(resource, None)
        api.delete_resources_by_prefix("api_test_by")
        self.assertRaises(api.NotFound, api.resource, "api_test_by_prefix")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09b_delete_resources_by_prefix(self):
        """ should allow deleting resources by tags """
        uploader.upload("tests/logo.png", public_id="api_test4", tags=["api_test_tag_for_delete"])
        resource = api.resource("api_test4")
        self.assertNotEqual(resource, None)
        api.delete_resources_by_tag("api_test_tag_for_delete")
        self.assertRaises(api.NotFound, api.resource, "api_test4")

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09c_delete_resources_by_transformations(self, mocker):
        """ should allow deleting resources by transformations """
        mocker.return_value = MOCK_RESPONSE

        api.delete_resources(['api_test', 'api_test2'], transformations=['c_crop,w_100'])
        self.assertEqual(mocker.call_args[0][0], 'DELETE')
        self.assertIn(('transformations', 'c_crop,w_100'), mocker.call_args[0][2])

        api.delete_all_resources(transformations=['c_crop,w_100', {"crop": "scale", "width": 107}])
        self.assertEqual(mocker.call_args[0][0], 'DELETE')
        self.assertEqual(mocker.call_args[0][2]['transformations'], 'c_crop,w_100|c_scale,w_107')

        api.delete_resources_by_prefix("api_test_by", transformations='c_crop,w_100')
        self.assertEqual(mocker.call_args[0][0], 'DELETE')
        self.assertEqual(mocker.call_args[0][2]['transformations'], 'c_crop,w_100')

        api.delete_resources_by_tag("api_test_tag", transformations=['c_crop,w_100'])
        self.assertEqual(mocker.call_args[0][0], 'DELETE')
        self.assertEqual(mocker.call_args[0][2]['transformations'], 'c_crop,w_100')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test10_tags(self):
        """ should allow listing tags """
        tags = api.tags()["tags"]
        self.assertIn("api_test_tag", tags)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test11_tags_prefix(self):
        """ should allow listing tag by prefix """
        tags = api.tags(prefix="api_test")["tags"]
        self.assertIn("api_test_tag", tags)
        tags = api.tags(prefix="api_test_no_such_tag")["tags"]
        self.assertEqual(len(tags), 0)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test12_transformations(self):
        """ should allow listing transformations """
        transformations = api.transformations(max_results=500)["transformations"]
        transformation = [tr for tr in transformations if tr["name"] == "c_scale,w_100"][0]

        self.assertIsNotNone(transformation)
        self.assertIs(transformation["used"], True)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test13_transformation_metadata(self):
        """ should allow getting transformation metadata """
        transformation = api.transformation("c_scale,w_100")
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["info"], [{"crop": "scale", "width": 100}])
        transformation = api.transformation({"crop": "scale", "width": 100})
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["info"], [{"crop": "scale", "width": 100}])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test14_transformation_update(self):
        """ should allow updating transformation allowed_for_strict """
        api.update_transformation("c_scale,w_100", allowed_for_strict=True)
        transformation = api.transformation("c_scale,w_100")
        self.assertNotEqual(transformation, None)
        self.assertIs(transformation["allowed_for_strict"], True)
        api.update_transformation("c_scale,w_100", allowed_for_strict=False)
        transformation = api.transformation("c_scale,w_100")
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["allowed_for_strict"], False)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15_transformation_create(self):
        """ should allow creating named transformation """
        api.create_transformation("api_test_transformation", {"crop": "scale", "width": 102})
        transformation = api.transformation("api_test_transformation")
        self.assertNotEqual(transformation, None)
        self.assertIs(transformation["allowed_for_strict"], True)
        self.assertEqual(transformation["info"], [{"crop": "scale", "width": 102}])
        self.assertEqual(transformation["used"], False)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test15a_transformation_unsafe_update(self):
        """ should allow unsafe update of named transformation """
        api.create_transformation("api_test_transformation3", {"crop": "scale", "width": 102})
        api.update_transformation("api_test_transformation3", unsafe_update={"crop": "scale", "width": 103})
        transformation = api.transformation("api_test_transformation3")
        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["info"], [{"crop": "scale", "width": 103}])
        self.assertEqual(transformation["used"], False)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test16_transformation_delete(self):
        """ should allow deleting named transformation """
        api.create_transformation("api_test_transformation2", {"crop": "scale", "width": 103})
        api.transformation("api_test_transformation2")
        api.delete_transformation("api_test_transformation2")
        self.assertRaises(api.NotFound, api.transformation, "api_test_transformation2")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test17_transformation_implicit(self):
        """ should allow deleting implicit transformation """
        api.transformation("c_scale,w_100")
        api.delete_transformation("c_scale,w_100")
        self.assertRaises(api.NotFound, api.transformation, "c_scale,w_100")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test18_usage(self):
        """ should support usage API """
        self.assertIn("last_updated", api.usage())

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skip("Skip delete all derived resources by default")
    def test19_delete_derived(self):
        """ should allow deleting all resource """
        uploader.upload("tests/logo.png", public_id="api_test5", eager=[{"width": 101, "crop": "scale"}])
        resource = api.resource("api_test5")
        self.assertNotEqual(resource, None)
        self.assertEqual(len(resource["derived"]), 1)
        api.delete_all_resources(keep_original=True)
        resource = api.resource("api_test5")
        self.assertNotEqual(resource, None)
        self.assertEqual(len(resource["derived"]), 0)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test20_manual_moderation(self):
        """ should support setting manual moderation status """
        resource = uploader.upload("tests/logo.png", moderation="manual")

        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")

        api_result = api.update(resource["public_id"], moderation_status="approved")
        self.assertEqual(api_result["moderation"][0]["status"], "approved")
        self.assertEqual(api_result["moderation"][0]["kind"], "manual")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test22_raw_conversion(self):
        """ should support requesting raw_convert """
        resource = uploader.upload("tests/docx.docx", resource_type="raw")
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update(resource["public_id"], raw_convert="illegal", resource_type="raw")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test23_categorization(self):
        """ should support requesting categorization """
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update("api_test", categorization="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test24_detection(self):
        """ should support requesting detection """
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update("api_test", detection="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test26_auto_tagging(self):
        """ should support requesting auto_tagging """
        with six.assertRaisesRegex(self, api.BadRequest, 'Must use'):
            api.update("api_test", auto_tagging=0.5)

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test26_1_ocr(self, mocker):
        """ should support requesting ocr """
        mocker.return_value = MOCK_RESPONSE
        api.update("api_test", ocr='adv_ocr')
        params = mocker.call_args[0][2]
        self.assertEqual(params['ocr'], 'adv_ocr')

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test27_start_at(self, mocker):
        """ should allow listing resources by start date """
        mocker.return_value = MOCK_RESPONSE
        start_at = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        api_repsonse = api.resources(type="upload", start_at=start_at, direction="asc")
        params = mocker.call_args[0][2]
        self.assertEqual(params['start_at'], start_at)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test28_create_list_upload_presets(self):
        """ should allow creating and listing upload_presets """
        api.create_upload_preset(name="api_test_upload_preset", folder="folder")
        api.create_upload_preset(name="api_test_upload_preset2", folder="folder2")
        api.create_upload_preset(name="api_test_upload_preset3", folder="folder3")

        api_response = api.upload_presets()
        presets = api_response["presets"]
        self.assertGreaterEqual(len(presets), 3)
        self.assertEqual(presets[0]["name"], "api_test_upload_preset3")
        self.assertEqual(presets[1]["name"], "api_test_upload_preset2")
        self.assertEqual(presets[2]["name"], "api_test_upload_preset")
        api.delete_upload_preset("api_test_upload_preset")
        api.delete_upload_preset("api_test_upload_preset2")
        api.delete_upload_preset("api_test_upload_preset3")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test29_get_upload_presets(self):
        """ should allow getting a single upload_preset """
        result = api.create_upload_preset(unsigned=True, folder="folder", width=100, crop="scale",
                                          tags=["a", "b", "c"], context={"a": "b", "c": "d"})
        name = result["name"]
        preset = api.upload_preset(name)
        self.assertEqual(preset["name"], name)
        self.assertIs(preset["unsigned"], True)
        settings = preset["settings"]
        self.assertEqual(settings["folder"], "folder")
        self.assertEqual(settings["transformation"], [{"width": 100, "crop": "scale"}])
        self.assertEqual(settings["context"], {"a": "b", "c": "d"})
        self.assertEqual(settings["tags"], ["a", "b", "c"])
        api.delete_upload_preset(name)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test30_create_list_upload_presets(self):
        """ should allow deleting upload_presets """
        api.create_upload_preset(name="api_test_upload_preset4", folder="folder")
        api.upload_preset("api_test_upload_preset4")
        api.delete_upload_preset("api_test_upload_preset4")
        with self.assertRaises(api.NotFound):
            api.upload_preset("api_test_upload_preset4")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test31_update_upload_presets(self):
        """ should allow getting a single upload_preset """
        result = api.create_upload_preset(folder="folder")
        name = result["name"]
        preset = api.upload_preset(name)
        settings = preset["settings"]
        settings.update({"colors": True, "unsigned": True, "disallow_public_id": True})
        api.update_upload_preset(name, **settings)
        preset = api.upload_preset(name)
        self.assertIs(preset["unsigned"], True)
        self.assertEqual(preset["settings"], {"folder": "folder", "colors": True, "disallow_public_id": True})
        api.delete_upload_preset(name)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test32_background_removal(self):
        """ should support requesting background_removal """
        with six.assertRaisesRegex(self, api.BadRequest, 'Illegal value'):
            api.update("api_test", background_removal="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skip("For this test to work, 'Auto-create folders' should be enabled in the Upload Settings, " +
                   "and the account should be empty of folders. " +
                   "Comment out this line if you really want to test it.")
    def test_folder_listing(self):
        """ should support listing folders """
        uploader.upload("tests/logo.png", public_id="test_folder1/item")
        uploader.upload("tests/logo.png", public_id="test_folder2/item")
        uploader.upload("tests/logo.png", public_id="test_folder1/test_subfolder1/item")
        uploader.upload("tests/logo.png", public_id="test_folder1/test_subfolder2/item")
        result = api.root_folders()
        self.assertEqual(result["folders"][0]["name"], "test_folder1")
        self.assertEqual(result["folders"][1]["name"], "test_folder2")
        result = api.subfolders("test_folder1")
        self.assertEqual(result["folders"][0]["path"], "test_folder1/test_subfolder1")
        self.assertEqual(result["folders"][1]["path"], "test_folder1/test_subfolder2")
        with six.assertRaisesRegex(self, api.NotFound):
            api.subfolders("test_folder")
        api.delete_resources_by_prefix("test_folder")

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
        uploader.upload("tests/logo.png", public_id="api_test_restore", backup=True)
        resource = api.resource("api_test_restore")
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["bytes"], 3381)
        api.delete_resources(["api_test_restore"])
        resource = api.resource("api_test_restore")
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["bytes"], 0)
        self.assertIs(resource["placeholder"], True)
        response = api.restore(["api_test_restore"])
        info = response["api_test_restore"]
        self.assertNotEqual(info, None)
        self.assertEqual(info["bytes"], 3381)
        resource = api.resource("api_test_restore")
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["bytes"], 3381)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_mapping(self):
        try:
            api.delete_upload_mapping("api_test_upload_mapping")
        except Exception:
            pass
        api.create_upload_mapping("api_test_upload_mapping", template="http://cloudinary.com")
        result = api.upload_mapping("api_test_upload_mapping")
        self.assertEqual(result["template"], "http://cloudinary.com")
        api.update_upload_mapping("api_test_upload_mapping", template="http://res.cloudinary.com")
        result = api.upload_mapping("api_test_upload_mapping")
        self.assertEqual(result["template"], "http://res.cloudinary.com")
        result = api.upload_mappings()
        self.assertIn({"folder": "api_test_upload_mapping", "template": "http://res.cloudinary.com"},
                      result["mappings"])
        api.delete_upload_mapping("api_test_upload_mapping")
        result = api.upload_mappings()
        self.assertNotIn("api_test_upload_mapping", [mapping.get("folder") for mapping in result["mappings"]])

if __name__ == '__main__':
    unittest.main()
