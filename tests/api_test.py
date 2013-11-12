import cloudinary
from cloudinary import uploader, utils, api
import unittest

class TestApi(unittest.TestCase):
    initialized = False
    def setUp(self):
        if TestApi.initialized: return
        TestApi.initialized = True
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
        uploader.upload("tests/logo.png", public_id="api_test", tags="api_test_tag", eager=[{"width": 100,"crop": "scale"}])
        uploader.upload("tests/logo.png", public_id="api_test2", tags="api_test_tag", eager=[{"width": 100,"crop": "scale"}])

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
        public_ids = [resource["public_id"] for resource in api.resources(type="upload", prefix="api_test")["resources"]]
        self.assertIn("api_test", public_ids)
        self.assertIn("api_test2", public_ids)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test06_resources_tag(self):
        """ should allow listing resources by tag """
        resource = [resource for resource in api.resources_by_tag("api_test_tag")["resources"] if resource["public_id"] == "api_test"][0]
        self.assertNotEqual(resource, None)

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

