import unittest
import cloudinary
from cloudinary import uploader, utils, api
from cloudinary.compat import PY3

class ApiTest(unittest.TestCase):
    initialized = False
    def setUp(self):
        if ApiTest.initialized: return
        ApiTest.initialized = True
        cloudinary.reset_config()
        if not cloudinary.config().api_secret: return
        try:
            api.delete_resources(["api_test", "api_test2", "api_test3"])
        except:
            pass
        try:
            api.delete_transformation("api_test_transformation")
        except:
            pass
        try:
            api.delete_transformation("api_test_transformation2")
        except:
            pass
        try:
            api.delete_transformation("api_test_transformation3")
        except:
            pass
        uploader.upload("tests/logo.png", public_id="api_test", tags="api_test_tag", context="key=value", eager=[{"width": 100,"crop": "scale"}])
        uploader.upload("tests/logo.png", public_id="api_test2", tags="api_test_tag", context="key=value", eager=[{"width": 100,"crop": "scale"}])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test01_resource_types(self):
        """ should allow listing resource_types """
        self.assertIn("image", api.resource_types()["resource_types"])
    
    test01_resource_types.tags = ['safe']
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test02_resources(self):
        """ should allow listing resources """
        resource = [resource for resource in api.resources()["resources"] if resource["public_id"] == "api_test"][0]
        self.assertNotEqual(resource, None)
        self.assertEqual(resource["type"], "upload" )

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
        resource = [resource for resource in api.resources(type="upload")["resources"] if resource["public_id"] == "api_test"][0]
        self.assertNotEqual(resource, None)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test05_resources_prefix(self):
        """ should allow listing resources by prefix """
        resources = api.resources(prefix = "api_test", context = True, tags = True, type = "upload")["resources"]
        public_ids = [resource["public_id"] for resource in resources]
        self.assertIn("api_test", public_ids)
        self.assertIn("api_test2", public_ids)
        self.assertIn(["api_test_tag"], [resource["tags"] for resource in resources])
        self.assertIn({"custom": {"key": "value"}}, [resource["context"] for resource in resources])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_resources_tag(self):
        """ should allow listing resources by tag """
        resources = api.resources_by_tag("api_test_tag", context = True, tags = True)["resources"]
        resource = [resource for resource in resources if resource["public_id"] == "api_test"][0]
        self.assertNotEqual(resource, None)
        self.assertIn(["api_test_tag"], [resource["tags"] for resource in resources])
        self.assertIn({"custom": {"key": "value"}}, [resource["context"] for resource in resources])
        
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06a_resources_by_ids(self):
        """ should allow listing resources by public ids """
        resources = api.resources_by_ids(["api_test", "api_test2"], context = True, tags = True)["resources"]
        public_ids = [resource["public_id"] for resource in resources]
        self.assertEqual(sorted(public_ids), ["api_test", "api_test2"])
        self.assertIn(["api_test_tag"], [resource["tags"] for resource in resources])
        self.assertIn({"custom": {"key": "value"}}, [resource["context"] for resource in resources])
        
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06b_resources_direction(self):
        """ should allow listing resources in both directions """
        asc_resources = api.resources(prefix = "api_test", direction = "asc", type = "upload")["resources"]
        desc_resources = api.resources(prefix = "api_test", direction = "desc", type = "upload")["resources"]
        asc_resources.reverse()
        self.assertEqual(asc_resources, desc_resources)
        asc_resources_alt = api.resources(prefix = "api_test", direction = 1, type = "upload")["resources"]
        desc_resources_alt = api.resources(prefix = "api_test", direction = -1, type = "upload")["resources"]
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
        uploader.upload("tests/logo.png", public_id="api_test3", eager=[{"width": 101,"crop": "scale"}])
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
        self.assertRaises(api.NotFound, api.resource, ("api_test3"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09a_delete_resources_by_prefix(self):
        """ should allow deleting resources by prefix """
        uploader.upload("tests/logo.png", public_id="api_test_by_prefix")
        resource = api.resource("api_test_by_prefix")
        self.assertNotEqual(resource, None)
        api.delete_resources_by_prefix("api_test_by")
        self.assertRaises(api.NotFound, api.resource, ("api_test_by_prefix"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test09b_delete_resources_by_prefix(self):
        """ should allow deleting resources by tags """
        uploader.upload("tests/logo.png", public_id="api_test4", tags=["api_test_tag_for_delete"])
        resource = api.resource("api_test4")
        self.assertNotEqual(resource, None)
        api.delete_resources_by_tag("api_test_tag_for_delete")
        self.assertRaises(api.NotFound, api.resource, ("api_test4"))

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
        transformation = [transformation for transformation in api.transformations()["transformations"] if transformation["name"] == "c_scale,w_100"][0]

        self.assertNotEqual(transformation, None)
        self.assertEqual(transformation["used"], True)

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
        self.assertEqual(transformation["allowed_for_strict"], True)
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
        self.assertEqual(transformation["allowed_for_strict"], True)
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
        self.assertRaises(api.NotFound, api.transformation, ("api_test_transformation2"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test17_transformation_implicit(self):
        """ should allow deleting implicit transformation """
        api.transformation("c_scale,w_100")
        api.delete_transformation("c_scale,w_100")
        self.assertRaises(api.NotFound, api.transformation, ("c_scale,w_100"))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test18_usage(self):
        """ should support usage API """
        self.assertIn("last_updated", api.usage())
        
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skip("Skip delete all derived resources by default")
    def test19_delete_derived(self):
        """ should allow deleting all resource """
        uploader.upload("tests/logo.png", public_id="api_test5", eager=[{"width": 101,"crop": "scale"}])
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
    def test21_ocr_info(self):
        """ should support requesting ocr info """
        with self.assertRaisesRegexp(api.BadRequest, 'Illegal value'): 
            api.update("api_test", ocr="illegal")
    
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test22_raw_conversion(self):
        """ should support requesting raw_convert """ 
        resource = uploader.upload("tests/docx.docx", resource_type="raw")
        with self.assertRaisesRegexp(api.BadRequest, 'Illegal value'): 
            api.update(resource["public_id"], raw_convert="illegal", resource_type="raw")
  
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test23_categorization(self):
        """ should support requesting categorization """
        with self.assertRaisesRegexp(api.BadRequest, 'Illegal value'): 
            api.update("api_test", categorization="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test24_detection(self):
        """ should support requesting detection """
        with self.assertRaisesRegexp(api.BadRequest, 'Illegal value'): 
            api.update("api_test", detection="illegal")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test25_similarity_search(self):
        """ should support requesting similarity_search """
        with self.assertRaisesRegexp(api.BadRequest, 'Illegal value'): 
            api.update("api_test", similarity_search="illegal")
  
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test26_auto_tagging(self):
        """ should support requesting auto_tagging """
        with self.assertRaisesRegexp(api.BadRequest, 'Must use'): 
            api.update("api_test", auto_tagging=0.5)

if __name__ == '__main__':
    unittest.main() 
