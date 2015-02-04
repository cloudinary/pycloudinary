import copy
import cloudinary.utils
import unittest
import re

class TestUtils(unittest.TestCase):
    def setUp(self):
        cloudinary.config(cloud_name = "test123", api_secret = "b", secure_distribution = None, private_cdn = False)

    def __test_cloudinary_url(self, public_id = "test", options = {}, expected_url = None, expected_options = {}):
        url, options = cloudinary.utils.cloudinary_url(public_id, **options)
        self.assertEqual(url, expected_url)
        self.assertEqual(options, expected_options)

    def test_cloud_name(self):
        """should use cloud_name from config"""
        self.__test_cloudinary_url(options = {}, expected_url = "http://res.cloudinary.com/test123/image/upload/test")

    def test_cloud_name_options(self):
        """should allow overriding cloud_name in options"""
        self.__test_cloudinary_url(options = {"cloud_name": "test321"}, expected_url = "http://res.cloudinary.com/test321/image/upload/test" )

    def test_secure_distribution(self):
        """should use default secure distribution if secure=True"""
        self.__test_cloudinary_url(options = {"secure": True}, expected_url =  "https://res.cloudinary.com/test123/image/upload/test" )

    def test_secure_distribution_overwrite(self):
        """should allow overwriting secure distribution if secure=True"""
        self.__test_cloudinary_url(options = {"secure": True, "secure_distribution": "something.else.com"}, expected_url =  "https://something.else.com/test123/image/upload/test" )

    def test_secure_distibution(self):
        """should take secure distribution from config if secure=True"""
        cloudinary.config().secure_distribution = "config.secure.distribution.com"
        self.__test_cloudinary_url(options = {"secure": True}, expected_url =  "https://config.secure.distribution.com/test123/image/upload/test" )

    def test_secure_akamai(self):
        """should default to akamai if secure is given with private_cdn and no secure_distribution"""
        self.__test_cloudinary_url(options = {"secure": True, "private_cdn": True}, expected_url =  "https://test123-res.cloudinary.com/image/upload/test" )

    def test_secure_non_akamai(self):
        """should not add cloud_name if private_cdn and secure non akamai secure_distribution"""
        self.__test_cloudinary_url(options = {"secure": True, "private_cdn": True, "secure_distribution": "something.cloudfront.net"}, expected_url =  "https://something.cloudfront.net/image/upload/test")

    def test_http_private_cdn(self):
        """should not add cloud_name if private_cdn and not secure"""
        self.__test_cloudinary_url(options = {"private_cdn": True}, expected_url =  "http://test123-res.cloudinary.com/image/upload/test")

    def test_format(self):
        """should use format from options"""
        self.__test_cloudinary_url(options = {"format": "jpg"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/test.jpg" )

    def test_crop(self):
        """should always use width and height from options"""
        self.__test_cloudinary_url(
            options = {"width": 100, "height": 100}, 
            expected_url = "http://res.cloudinary.com/test123/image/upload/h_100,w_100/test",
            expected_options = {"width": 100, "height": 100} )
        self.__test_cloudinary_url(
            options = {"width": 100, "height": 100, "crop": "crop"}, 
            expected_url = "http://res.cloudinary.com/test123/image/upload/c_crop,h_100,w_100/test",
            expected_options = {"width": 100, "height": 100} )

    def test_html_width_height_on_crop_fit_limit(self):
        """should not pass width and height to html in case of fit or limit crop"""
        self.__test_cloudinary_url(options = {"width": 100, "height": 100, "crop": "limit"}, expected_url = "http://res.cloudinary.com/test123/image/upload/c_limit,h_100,w_100/test" )
        self.__test_cloudinary_url(options = {"width": 100, "height": 100, "crop": "fit"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/c_fit,h_100,w_100/test" )

    def test_html_width_height_on_angle(self):
        """should not pass width and height to html in case angle was used"""
        self.__test_cloudinary_url(options = {"width": 100, "height": 100, "crop": "scale", "angle": "auto"}, expected_url = "http://res.cloudinary.com/test123/image/upload/a_auto,c_scale,h_100,w_100/test" )

    def test_various_options(self):
        """should use x, y, radius, prefix, gravity and quality from options"""
        self.__test_cloudinary_url(options = {"x": 1, "y": 2, "opacity": 20, "radius": 3, "gravity": "center", "quality": 0.4, "prefix": "a"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/g_center,o_20,p_a,q_0.4,r_3,x_1,y_2/test" )

    def test_transformation_simple(self):
        """should support named tranformation"""
        self.__test_cloudinary_url(options = {"transformation": "blip"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/t_blip/test" )

    def test_transformation_array(self):
        """should support array of named tranformations"""
        self.__test_cloudinary_url(options = {"transformation": ["blip", "blop"]}, expected_url =  "http://res.cloudinary.com/test123/image/upload/t_blip.blop/test" )

    def test_base_transformations(self):
        """should support base tranformation"""
        self.__test_cloudinary_url(
            options = {"transformation": {"x": 100, "y": 100, "crop": "fill"}, "crop": "crop", "width": 100},
            expected_url = "http://res.cloudinary.com/test123/image/upload/c_fill,x_100,y_100/c_crop,w_100/test",
            expected_options = {"width": 100})

    def test_base_transformation_array(self):
        """should support array of base tranformations"""
        options = {"transformation": [{"x": 100, "y": 100, "width": 200, "crop": "fill"}, {"radius": 10}], "crop": "crop", "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": 100})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_fill,w_200,x_100,y_100/r_10/c_crop,w_100/test" )

    def test_no_empty_transformation(self):
        """should not include empty tranformations"""
        self.__test_cloudinary_url(options = {"transformation": [{}, {"x": 100, "y": 100, "crop": "fill"}, {}]}, expected_url =  "http://res.cloudinary.com/test123/image/upload/c_fill,x_100,y_100/test" )

    def test_size(self):
        """should support size"""
        options = {"size": "10x10", "crop": "crop"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": "10", "height": "10"})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_crop,h_10,w_10/test" )

    def test_type(self):
        """should use type from options"""
        self.__test_cloudinary_url(options = {"type": "facebook"}, expected_url =  "http://res.cloudinary.com/test123/image/facebook/test" )

    def test_resource_type(self):
        """should use resource_type from options"""
        self.__test_cloudinary_url(options = {"resource_type": "raw"}, expected_url =  "http://res.cloudinary.com/test123/raw/upload/test" )

    def test_ignore_http(self):
        """should ignore http links only if type is not given or is asset"""
        options = {}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://test" )
        options = {"type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/fetch/http://test" )

    def test_fetch(self):
        """should escape fetch urls"""
        options = {"type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://blah.com/hello?a=b", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/fetch/http://blah.com/hello%3Fa%3Db" )

    def test_http_escape(self):
        """should escape http urls"""
        options = {"type": "youtube"}
        result, options = cloudinary.utils.cloudinary_url("http://www.youtube.com/watch?v=d9NF2edxy-M", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/youtube/http://www.youtube.com/watch%3Fv%3Dd9NF2edxy-M" )

    def test_cname(self):
        """should support extenal cname"""
        self.__test_cloudinary_url(options = {"cname": "hello.com"}, expected_url =  "http://hello.com/test123/image/upload/test" )

    def test_cname_subdomain(self):
        """should support extenal cname with cdn_subdomain on"""
        self.__test_cloudinary_url(options = {"cname": "hello.com", "cdn_subdomain": True}, expected_url =  "http://a2.hello.com/test123/image/upload/test" )

    def test_background(self):
        """should support background"""
        self.__test_cloudinary_url(options = {"background": "red"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/b_red/test" )
        self.__test_cloudinary_url(options = {"background": "#112233"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/b_rgb:112233/test" )

    def test_default_image(self):
        """should support default_image"""
        self.__test_cloudinary_url(options = {"default_image": "default"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/d_default/test" )

    def test_angle(self):
        """should support angle"""
        self.__test_cloudinary_url(options = {"angle": 12}, expected_url =  "http://res.cloudinary.com/test123/image/upload/a_12/test" )

    def test_overlay(self):
        """should support overlay"""
        self.__test_cloudinary_url(options = {"overlay": "text:hello"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/l_text:hello/test" )
        # Should not pass width height to HTML with overlay
        self.__test_cloudinary_url(options = {"overlay": "text:hello", "height": 100, "width": 100}, expected_url =  "http://res.cloudinary.com/test123/image/upload/h_100,l_text:hello,w_100/test" )

    def test_underlay(self):
        """should support underlay"""
        self.__test_cloudinary_url(options = {"underlay": "text:hello"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/u_text:hello/test" )
        # Should not pass width height to HTML with underlay
        self.__test_cloudinary_url(options = {"underlay": "text:hello", "height": 100, "width": 100}, expected_url =  "http://res.cloudinary.com/test123/image/upload/h_100,u_text:hello,w_100/test" )

    def test_fetch_format(self):
        """should support format for fetch urls"""
        self.__test_cloudinary_url(public_id = "http://cloudinary.com/images/logo.png",
            options = {"format": "jpg", "type": "fetch"}, 
            expected_url =  "http://res.cloudinary.com/test123/image/fetch/f_jpg/http://cloudinary.com/images/logo.png" )

    def test_effect(self):
        """should support effect"""
        self.__test_cloudinary_url(options = {"effect": "sepia"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/e_sepia/test" )

    def test_effect_with_dict(self):
        """should support effect with dict"""
        self.__test_cloudinary_url(options = {"effect": {"sepia": 10}}, expected_url =  "http://res.cloudinary.com/test123/image/upload/e_sepia:10/test" )

    def test_effect_with_array(self):
        """should support effect with array"""
        self.__test_cloudinary_url(options = {"effect": ["sepia", 10]}, expected_url =  "http://res.cloudinary.com/test123/image/upload/e_sepia:10/test" )

    def test_density(self):
        """should support density"""
        self.__test_cloudinary_url(options = {"density": 150}, expected_url =  "http://res.cloudinary.com/test123/image/upload/dn_150/test" )

    def test_page(self):
        """should support page"""
        self.__test_cloudinary_url(options = {"page": 3}, expected_url =  "http://res.cloudinary.com/test123/image/upload/pg_3/test" )

    def test_border(self):
        """should support border"""
        self.__test_cloudinary_url(options = {"border": {"width": 5}}, expected_url =  "http://res.cloudinary.com/test123/image/upload/bo_5px_solid_black/test" )
        self.__test_cloudinary_url(options = {"border": {"width": 5, "color": "#ffaabbdd"}}, expected_url =  "http://res.cloudinary.com/test123/image/upload/bo_5px_solid_rgb:ffaabbdd/test" )
        self.__test_cloudinary_url(options = {"border": "1px_solid_blue"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/bo_1px_solid_blue/test" )

    def test_flags(self):
        """should support flags"""
        self.__test_cloudinary_url(options = {"flags": "abc"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/fl_abc/test" )
        self.__test_cloudinary_url(options = {"flags": ["abc", "def"]}, expected_url =  "http://res.cloudinary.com/test123/image/upload/fl_abc.def/test" )

    def test_dpr(self):
        """should support dpr (device pixel radio)"""
        self.__test_cloudinary_url(options = {"dpr": "2.0"}, expected_url =  "http://res.cloudinary.com/test123/image/upload/dpr_2.0/test" )

    def test_folder_version(self):
        """should add version if public_id contains / """
        self.__test_cloudinary_url(public_id = "folder/test", expected_url = "http://res.cloudinary.com/test123/image/upload/v1/folder/test")
        self.__test_cloudinary_url(public_id = "folder/test", options = {"version": 123}, expected_url = "http://res.cloudinary.com/test123/image/upload/v123/folder/test")
        self.__test_cloudinary_url(public_id = "v1234/test", expected_url = "http://res.cloudinary.com/test123/image/upload/v1234/test")

    def test_shorten(self):
        self.__test_cloudinary_url(options = {"shorten": True}, expected_url = "http://res.cloudinary.com/test123/iu/test")
        self.__test_cloudinary_url(options = {"shorten": True, "type": "private"}, expected_url = "http://res.cloudinary.com/test123/image/private/test")
    
    def test_signed_url(self):
        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"version": 1234, "transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True}, 
            expected_url = "http://res.cloudinary.com/test123/image/upload/s--Ai4Znfl3--/c_crop,h_20,w_10/v1234/image.jpg")

        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"version": 1234, "sign_url": True}, 
            expected_url = "http://res.cloudinary.com/test123/image/upload/s----SjmNDA--/v1234/image.jpg")

        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True}, 
            expected_url = "http://res.cloudinary.com/test123/image/upload/s--Ai4Znfl3--/c_crop,h_20,w_10/image.jpg")

        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"type": "authenticated", "transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True}, 
            expected_url = "http://res.cloudinary.com/test123/image/authenticated/s--Ai4Znfl3--/c_crop,h_20,w_10/image.jpg")

        
        self.__test_cloudinary_url(
            public_id = "http://google.com/path/to/image.png",
            options = {"version": 1234, "type": "fetch", "sign_url": True}, 
            expected_url = "http://res.cloudinary.com/test123/image/fetch/s--hH_YcbiS--/v1234/http://google.com/path/to/image.png")
    
    def test_disallow_url_suffix_in_shared_distribution(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix = "hello")


    def test_should_allow_explicit_private_cdn_false(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix = "hello", private_cdn = False)


    def test_disallow_url_suffix_in_non_upload_types(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix = "hello", private_cdn = True, type = "facebook")


    def test_disallow_url_suffix_with_slash_or_dot(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix = "hello/world", private_cdn = True)
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix = "hello.world", private_cdn = True)


    def test_support_url_suffix_for_private_cdn(self):    
        self.__test_cloudinary_url(options = {"url_suffix": "hello", "private_cdn": True}, expected_url = "http://test123-res.cloudinary.com/images/test/hello")
        self.__test_cloudinary_url(options = {"url_suffix": "hello", "angle": 0, "private_cdn": True}, expected_url = "http://test123-res.cloudinary.com/images/a_0/test/hello")


    def test_put_format_after_url_suffix(self):
        self.__test_cloudinary_url(options = {"url_suffix": "hello", "private_cdn": True, "format": "jpg"}, expected_url = "http://test123-res.cloudinary.com/images/test/hello.jpg")


    def test_not_sign_the_url_suffix(self):
        url, options = cloudinary.utils.cloudinary_url("test", format = "jpg", sign_url = True)
        expected_signature = re.search(r's--[0-9A-Za-z_-]{8}--', url)
        self.__test_cloudinary_url(options = {"url_suffix": "hello", "private_cdn": True, "format": "jpg", "sign_url": True}, expected_url = "http://test123-res.cloudinary.com/images/" + expected_signature.group(0) + "/test/hello.jpg")

        url, options = cloudinary.utils.cloudinary_url("test", format = "jpg", angle = 0, sign_url = True)
        expected_signature = re.search(r's--[0-9A-Za-z_-]{8}--', url)
        self.__test_cloudinary_url(options = {"url_suffix": "hello", "private_cdn": True, "format": "jpg", "angle": 0, "sign_url": True}, expected_url = "http://test123-res.cloudinary.com/images/" + expected_signature.group(0) + "/a_0/test/hello.jpg")


    def test_support_url_suffix_for_raw_uploads(self):    
        self.__test_cloudinary_url(options = {"url_suffix": "hello", "private_cdn": True, "resource_type": "raw"}, expected_url = "http://test123-res.cloudinary.com/files/test/hello")


    def test_support_use_root_path_for_shared_cdn(self):
        self.__test_cloudinary_url(options = {"use_root_path": True, "private_cdn": False}, expected_url = "http://res.cloudinary.com/test123/test")
        self.__test_cloudinary_url(options = {"use_root_path": True, "private_cdn": False, "angle": 0}, expected_url = "http://res.cloudinary.com/test123/a_0/test")


    def test_support_use_root_path_for_private_cdn(self):
        self.__test_cloudinary_url(options = {"use_root_path": True, "private_cdn": True}, expected_url = "http://test123-res.cloudinary.com/test")
        self.__test_cloudinary_url(options = {"use_root_path": True, "private_cdn": True, "angle": 0}, expected_url = "http://test123-res.cloudinary.com/a_0/test")


    def test_support_use_root_path_together_with_url_suffix_for_private_cdn(self):
        self.__test_cloudinary_url(options = {"use_root_path": True, "url_suffix": "hello", "private_cdn": True}, expected_url = "http://test123-res.cloudinary.com/test/hello")


    def test_disallow_use_root_path_if_not_image_upload(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", use_root_path = True, private_cdn = True, type = "facebook")
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", use_root_path = True, private_cdn = True, resource_type = "raw")

    def test_support_cdn_subdomain_with_secure_on_if_using_shared_domain(self):
        self.__test_cloudinary_url(options = {"secure": True, "cdn_subdomain": True}, expected_url = "https://res-2.cloudinary.com/test123/image/upload/test")


    def support_secure_cdn_subdomain_false_override_with_secure(self):
        self.__test_cloudinary_url(options = {"secure": True, "cdn_subdomain": True, "secure_cdn_subdomain": False}, expected_url = "https://res.cloudinary.com/test123/image/upload/test")

    def test_support_secure_cdn_subdomain_true_override_with_secure(self):
        self.__test_cloudinary_url(options = {"secure": True, "cdn_subdomain": True, "secure_cdn_subdomain": True,  "private_cdn": True}, expected_url = "https://test123-res-2.cloudinary.com/image/upload/test")

    def test_escape_public_id(self):
        """ should escape public_ids """
        tests = {
            "a b": "a%20b",
            "a+b": "a%2Bb",
            "a%20b": "a%20b",
            "a-b": "a-b",
            "a??b": "a%3F%3Fb"
        }
        for source, target in tests.items():
            result, options = cloudinary.utils.cloudinary_url(source)
            self.assertEquals("http://res.cloudinary.com/test123/image/upload/" + target, result)

    def test_responsive_width(self):
        """should support responsive width"""
        options = {"width": 100, "height": 100, "crop": "crop", "responsive_width": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"responsive": True})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_crop,h_100,w_100/c_limit,w_auto/test" )
        cloudinary.config(responsive_width_transformation={"width": "auto", "crop": "pad"})
        options = {"width": 100, "height": 100, "crop": "crop", "responsive_width": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"responsive": True})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_crop,h_100,w_100/c_pad,w_auto/test" )

if __name__ == '__main__':
    unittest.main()
