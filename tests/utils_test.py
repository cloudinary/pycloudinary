import cloudinary.utils
import unittest
import re
from fractions import Fraction
from cloudinary.compat import cldrange

DEFAULT_ROOT_PATH = 'http://res.cloudinary.com/test123/'
DEFAULT_UPLOAD_PATH = 'http://res.cloudinary.com/test123/image/upload/'
VIDEO_UPLOAD_PATH = 'http://res.cloudinary.com/test123/video/upload/'

class TestUtils(unittest.TestCase):
    def setUp(self):
        cloudinary.config(cloud_name = "test123", api_key = "a", api_secret = "b", secure_distribution = None, private_cdn = False)

    def __test_cloudinary_url(self, public_id = "test", options = {}, expected_url = None, expected_options = {}):
        url, options = cloudinary.utils.cloudinary_url(public_id, **options)
        self.assertEqual(url, expected_url)
        self.assertEqual(options, expected_options)

    def test_cloud_name(self):
        """should use cloud_name from config"""
        self.__test_cloudinary_url(options = {}, expected_url = DEFAULT_UPLOAD_PATH + "test")

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
        self.__test_cloudinary_url(options = {"format": "jpg"}, expected_url =  DEFAULT_UPLOAD_PATH + "test.jpg" )

    def test_crop(self):
        """should always use width and height from options"""
        self.__test_cloudinary_url(
            options = {"width": 100, "height": 100}, 
            expected_url = DEFAULT_UPLOAD_PATH + "h_100,w_100/test",
            expected_options = {"width": 100, "height": 100} )
        self.__test_cloudinary_url(
            options = {"width": 100, "height": 100, "crop": "crop"}, 
            expected_url = DEFAULT_UPLOAD_PATH + "c_crop,h_100,w_100/test",
            expected_options = {"width": 100, "height": 100} )

    def test_html_width_height_on_crop_fit_limit(self):
        """should not pass width and height to html in case of fit or limit crop"""
        self.__test_cloudinary_url(options = {"width": 100, "height": 100, "crop": "limit"}, expected_url = DEFAULT_UPLOAD_PATH + "c_limit,h_100,w_100/test" )
        self.__test_cloudinary_url(options = {"width": 100, "height": 100, "crop": "fit"}, expected_url =  DEFAULT_UPLOAD_PATH + "c_fit,h_100,w_100/test" )

    def test_html_width_height_on_angle(self):
        """should not pass width and height to html in case angle was used"""
        self.__test_cloudinary_url(options = {"width": 100, "height": 100, "crop": "scale", "angle": "auto"}, expected_url = DEFAULT_UPLOAD_PATH + "a_auto,c_scale,h_100,w_100/test" )

    def test_various_options(self):
        """should use x, y, radius, prefix, gravity and quality from options"""
        self.__test_cloudinary_url(options = {"x": 1, "y": 2, "opacity": 20, "radius": 3, "gravity": "center", "quality": 0.4, "prefix": "a"}, expected_url =  DEFAULT_UPLOAD_PATH + "g_center,o_20,p_a,q_0.4,r_3,x_1,y_2/test" )

    def test_transformation_simple(self):
        """should support named tranformation"""
        self.__test_cloudinary_url(options = {"transformation": "blip"}, expected_url =  DEFAULT_UPLOAD_PATH + "t_blip/test" )

    def test_transformation_array(self):
        """should support array of named tranformations"""
        self.__test_cloudinary_url(options = {"transformation": ["blip", "blop"]}, expected_url =  DEFAULT_UPLOAD_PATH + "t_blip.blop/test" )

    def test_base_transformations(self):
        """should support base tranformation"""
        self.__test_cloudinary_url(
            options = {"transformation": {"x": 100, "y": 100, "crop": "fill"}, "crop": "crop", "width": 100},
            expected_url = DEFAULT_UPLOAD_PATH + "c_fill,x_100,y_100/c_crop,w_100/test",
            expected_options = {"width": 100})

    def test_base_transformation_array(self):
        """should support array of base tranformations"""
        options = {"transformation": [{"x": 100, "y": 100, "width": 200, "crop": "fill"}, {"radius": 10}], "crop": "crop", "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": 100})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_fill,w_200,x_100,y_100/r_10/c_crop,w_100/test" )

    def test_no_empty_transformation(self):
        """should not include empty tranformations"""
        self.__test_cloudinary_url(options = {"transformation": [{}, {"x": 100, "y": 100, "crop": "fill"}, {}]}, expected_url =  DEFAULT_UPLOAD_PATH + "c_fill,x_100,y_100/test" )

    def test_size(self):
        """should support size"""
        options = {"size": "10x10", "crop": "crop"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": "10", "height": "10"})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_crop,h_10,w_10/test" )

    def test_type(self):
        """should use type from options"""
        self.__test_cloudinary_url(options = {"type": "facebook"}, expected_url =  DEFAULT_ROOT_PATH + "image/facebook/test" )

    def test_resource_type(self):
        """should use resource_type from options"""
        self.__test_cloudinary_url(options = {"resource_type": "raw"}, expected_url =  DEFAULT_ROOT_PATH + "raw/upload/test" )

    def test_ignore_http(self):
        """should ignore http links only if type is not given or is asset"""
        options = {}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://test" )
        options = {"type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, DEFAULT_ROOT_PATH + "image/fetch/http://test" )

    def test_fetch(self):
        """should escape fetch urls"""
        options = {"type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://blah.com/hello?a=b", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, DEFAULT_ROOT_PATH + "image/fetch/http://blah.com/hello%3Fa%3Db" )

    def test_http_escape(self):
        """should escape http urls"""
        options = {"type": "youtube"}
        result, options = cloudinary.utils.cloudinary_url("http://www.youtube.com/watch?v=d9NF2edxy-M", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, DEFAULT_ROOT_PATH + "image/youtube/http://www.youtube.com/watch%3Fv%3Dd9NF2edxy-M" )

    def test_cname(self):
        """should support extenal cname"""
        self.__test_cloudinary_url(options = {"cname": "hello.com"}, expected_url =  "http://hello.com/test123/image/upload/test" )

    def test_cname_subdomain(self):
        """should support extenal cname with cdn_subdomain on"""
        self.__test_cloudinary_url(options = {"cname": "hello.com", "cdn_subdomain": True}, expected_url =  "http://a2.hello.com/test123/image/upload/test" )

    def test_background(self):
        """should support background"""
        self.__test_cloudinary_url(options = {"background": "red"}, expected_url =  DEFAULT_UPLOAD_PATH + "b_red/test" )
        self.__test_cloudinary_url(options = {"background": "#112233"}, expected_url =  DEFAULT_UPLOAD_PATH + "b_rgb:112233/test" )

    def test_default_image(self):
        """should support default_image"""
        self.__test_cloudinary_url(options = {"default_image": "default"}, expected_url =  DEFAULT_UPLOAD_PATH + "d_default/test" )

    def test_angle(self):
        """should support angle"""
        self.__test_cloudinary_url(options = {"angle": 12}, expected_url =  DEFAULT_UPLOAD_PATH + "a_12/test" )

    def test_overlay(self):
        """should support overlay"""
        self.__test_cloudinary_url(options = {"overlay": "text:hello"}, expected_url =  DEFAULT_UPLOAD_PATH + "l_text:hello/test" )
        # Should not pass width height to HTML with overlay
        self.__test_cloudinary_url(options = {"overlay": "text:hello", "height": 100, "width": 100}, expected_url =  DEFAULT_UPLOAD_PATH + "h_100,l_text:hello,w_100/test" )

        self.__test_cloudinary_url(options = {"overlay": {"font_family": "arial", "font_size": 20, "text": "hello"}, "height": 100, "width": 100}, expected_url =  DEFAULT_UPLOAD_PATH + "h_100,l_text:arial_20:hello,w_100/test" )

    def test_underlay(self):
        """should support underlay"""
        self.__test_cloudinary_url(options = {"underlay": "text:hello"}, expected_url =  DEFAULT_UPLOAD_PATH + "u_text:hello/test" )
        # Should not pass width height to HTML with underlay
        self.__test_cloudinary_url(options = {"underlay": "text:hello", "height": 100, "width": 100}, expected_url =  DEFAULT_UPLOAD_PATH + "h_100,u_text:hello,w_100/test" )

    def test_fetch_format(self):
        """should support format for fetch urls"""
        self.__test_cloudinary_url(public_id = "http://cloudinary.com/images/logo.png",
            options = {"format": "jpg", "type": "fetch"}, 
            expected_url =  DEFAULT_ROOT_PATH + "image/fetch/f_jpg/http://cloudinary.com/images/logo.png" )

    def test_effect(self):
        """should support effect"""
        self.__test_cloudinary_url(options = {"effect": "sepia"}, expected_url =  DEFAULT_UPLOAD_PATH + "e_sepia/test" )

    def test_effect_with_dict(self):
        """should support effect with dict"""
        self.__test_cloudinary_url(options = {"effect": {"sepia": 10}}, expected_url =  DEFAULT_UPLOAD_PATH + "e_sepia:10/test" )

    def test_effect_with_array(self):
        """should support effect with array"""
        self.__test_cloudinary_url(options = {"effect": ["sepia", 10]}, expected_url =  DEFAULT_UPLOAD_PATH + "e_sepia:10/test" )

    def test_density(self):
        """should support density"""
        self.__test_cloudinary_url(options = {"density": 150}, expected_url =  DEFAULT_UPLOAD_PATH + "dn_150/test" )

    def test_page(self):
        """should support page"""
        self.__test_cloudinary_url(options = {"page": 3}, expected_url =  DEFAULT_UPLOAD_PATH + "pg_3/test" )

    def test_border(self):
        """should support border"""
        self.__test_cloudinary_url(options = {"border": {"width": 5}}, expected_url =  DEFAULT_UPLOAD_PATH + "bo_5px_solid_black/test" )
        self.__test_cloudinary_url(options = {"border": {"width": 5, "color": "#ffaabbdd"}}, expected_url =  DEFAULT_UPLOAD_PATH + "bo_5px_solid_rgb:ffaabbdd/test" )
        self.__test_cloudinary_url(options = {"border": "1px_solid_blue"}, expected_url =  DEFAULT_UPLOAD_PATH + "bo_1px_solid_blue/test" )

    def test_flags(self):
        """should support flags"""
        self.__test_cloudinary_url(options = {"flags": "abc"}, expected_url =  DEFAULT_UPLOAD_PATH + "fl_abc/test" )
        self.__test_cloudinary_url(options = {"flags": ["abc", "def"]}, expected_url =  DEFAULT_UPLOAD_PATH + "fl_abc.def/test" )

    def test_dpr(self):
        """should support dpr (device pixel radio)"""
        self.__test_cloudinary_url(options = {"dpr": "2.0"}, expected_url =  DEFAULT_UPLOAD_PATH + "dpr_2.0/test" )

    def test_folder_version(self):
        """should add version if public_id contains / """
        self.__test_cloudinary_url(public_id = "folder/test", expected_url = DEFAULT_UPLOAD_PATH + "v1/folder/test")
        self.__test_cloudinary_url(public_id = "folder/test", options = {"version": 123}, expected_url = DEFAULT_UPLOAD_PATH + "v123/folder/test")
        self.__test_cloudinary_url(public_id = "v1234/test", expected_url = DEFAULT_UPLOAD_PATH + "v1234/test")

    def test_shorten(self):
        self.__test_cloudinary_url(options = {"shorten": True}, expected_url = DEFAULT_ROOT_PATH + "iu/test")
        self.__test_cloudinary_url(options = {"shorten": True, "type": "private"}, expected_url = DEFAULT_ROOT_PATH + "image/private/test")
    
    def test_signed_url(self):
        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"version": 1234, "transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True}, 
            expected_url = DEFAULT_UPLOAD_PATH + "s--Ai4Znfl3--/c_crop,h_20,w_10/v1234/image.jpg")

        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"version": 1234, "sign_url": True}, 
            expected_url = DEFAULT_UPLOAD_PATH + "s----SjmNDA--/v1234/image.jpg")

        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True}, 
            expected_url = DEFAULT_UPLOAD_PATH + "s--Ai4Znfl3--/c_crop,h_20,w_10/image.jpg")

        self.__test_cloudinary_url(
            public_id = "image.jpg",
            options = {"type": "authenticated", "transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True}, 
            expected_url = DEFAULT_ROOT_PATH + "image/authenticated/s--Ai4Znfl3--/c_crop,h_20,w_10/image.jpg")

        
        self.__test_cloudinary_url(
            public_id = "http://google.com/path/to/image.png",
            options = {"version": 1234, "type": "fetch", "sign_url": True}, 
            expected_url = DEFAULT_ROOT_PATH + "image/fetch/s--hH_YcbiS--/v1234/http://google.com/path/to/image.png")
    
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
        self.__test_cloudinary_url(options = {"use_root_path": True, "private_cdn": False}, expected_url = DEFAULT_ROOT_PATH + "test")
        self.__test_cloudinary_url(options = {"use_root_path": True, "private_cdn": False, "angle": 0}, expected_url = DEFAULT_ROOT_PATH + "a_0/test")


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
            self.assertEqual(DEFAULT_UPLOAD_PATH + "" + target, result)

    def test_responsive_width(self):
        """should support responsive width"""
        options = {"width": 100, "height": 100, "crop": "crop", "responsive_width": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"responsive": True})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_crop,h_100,w_100/c_limit,w_auto/test" )
        cloudinary.config(responsive_width_transformation={"width": "auto", "crop": "pad"})
        options = {"width": 100, "height": 100, "crop": "crop", "responsive_width": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"responsive": True})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_crop,h_100,w_100/c_pad,w_auto/test" )

    def test_norm_range_value(self) :
        # should parse integer range values
        self.assertEqual(cloudinary.utils.norm_range_value("200"), "200")
        # should parse float range values
        self.assertEqual(cloudinary.utils.norm_range_value("200.0"), "200.0")
        # should parse a percent range value
        self.assertEqual(cloudinary.utils.norm_range_value("20p"), "20p")
        self.assertEqual(cloudinary.utils.norm_range_value("20P"), "20p")
        self.assertEqual(cloudinary.utils.norm_range_value("20%"), "20p")
        self.assertEqual(cloudinary.utils.norm_range_value("p"), None)

    def test_video_codec(self):
        # should support a string value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_codec': 'auto'}, expected_url=VIDEO_UPLOAD_PATH + "vc_auto/video_id")
        # should support a hash value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_codec': {'codec': 'h264', 'profile': 'basic', 'level': '3.1' }},
                              expected_url=VIDEO_UPLOAD_PATH + "vc_h264:basic:3.1/video_id")

    def test_audio_codec(self):
        # should support a string value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'audio_codec': 'acc'}, expected_url=VIDEO_UPLOAD_PATH + "ac_acc/video_id")

    def test_bit_rate(self):
        # should support an integer value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'bit_rate': 2048}, expected_url=VIDEO_UPLOAD_PATH + "br_2048/video_id")
        # should support "<integer>k" 
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'bit_rate': '44k'}, expected_url=VIDEO_UPLOAD_PATH + "br_44k/video_id")
        # should support "<integer>m"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'bit_rate': '1m'}, expected_url=VIDEO_UPLOAD_PATH + "br_1m/video_id")

    def test_audio_frequency(self):
        # should support an integer value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'audio_frequency': 44100}, expected_url=VIDEO_UPLOAD_PATH + "af_44100/video_id")

    def test_video_sampling(self):
        # should support an integer value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_sampling': 20}, expected_url=VIDEO_UPLOAD_PATH + "vs_20/video_id")
        # should support an string value in the a form of \"<float>s\"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_sampling': "2.3s"}, expected_url=VIDEO_UPLOAD_PATH + "vs_2.3s/video_id")

    def test_start_offset(self):
        # should support decimal seconds 
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': 2.63}, expected_url=VIDEO_UPLOAD_PATH + "so_2.63/video_id")
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': '2.63'}, expected_url=VIDEO_UPLOAD_PATH + "so_2.63/video_id")
        # should support percents of the video length as "<number>p"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': '35p'}, expected_url=VIDEO_UPLOAD_PATH + "so_35p/video_id")
        # should support percents of the video length as "<number>%"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': '35%'}, expected_url=VIDEO_UPLOAD_PATH + "so_35p/video_id")

    def test_end_offset(self):
        # should support decimal seconds 
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': 2.63}, expected_url=VIDEO_UPLOAD_PATH + "eo_2.63/video_id")
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': '2.63'}, expected_url=VIDEO_UPLOAD_PATH + "eo_2.63/video_id")
        # should support percents of the video length as "<number>p"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': '35p'}, expected_url=VIDEO_UPLOAD_PATH + "eo_35p/video_id")
        # should support percents of the video length as "<number>%"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': '35%'}, expected_url=VIDEO_UPLOAD_PATH + "eo_35p/video_id")

    def test_duration(self):
        # should support decimal seconds 
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': 2.63}, expected_url=VIDEO_UPLOAD_PATH + "du_2.63/video_id")
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': '2.63'}, expected_url=VIDEO_UPLOAD_PATH + "du_2.63/video_id")
        # should support percents of the video length as "<number>p"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': '35p'}, expected_url=VIDEO_UPLOAD_PATH + "du_35p/video_id")
        # should support percents of the video length as "<number>%"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': '35%'}, expected_url=VIDEO_UPLOAD_PATH + "du_35p/video_id")

    def test_offset(self):
        test_cases = {
            'eo_3.21,so_2.66': '2.66..3.21',
            'eo_3.22,so_2.67': (2.67, 3.22),
            'eo_70p,so_35p': ('35%', '70%'),
            'eo_71p,so_36p': ('36p', '71p'),
            'eo_70.5p,so_35.5p': ['35.5p', '70.5p']
        }
        for transformation, offset in test_cases.items():
          self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'offset': offset}, expected_url=VIDEO_UPLOAD_PATH + transformation + "/video_id")

    def test_user_agent(self):
        agent = cloudinary.get_user_agent()
        platform = 'MyPlatform/1.2.3 (Test code)'
        self.assertRegexpMatches(agent, 'CloudinaryPython/\d\.\d+\.\d+')
        temp = cloudinary.USER_PLATFORM
        cloudinary.USER_PLATFORM = platform
        result = cloudinary.get_user_agent()
        cloudinary.USER_PLATFORM = temp  # restore value before assertion
        self.assertEqual(result, platform + ' ' + agent)

    def test_aspect_ratio(self):
        self.__test_cloudinary_url(
            public_id = "test",
            options = {"aspect_ratio": "1.0"}, 
            expected_url = DEFAULT_UPLOAD_PATH + "ar_1.0/test")
        self.__test_cloudinary_url(
            public_id = "test",
            options = {"aspect_ratio": "3:2"}, 
            expected_url = DEFAULT_UPLOAD_PATH + "ar_3:2/test")
        self.__test_cloudinary_url(
            public_id = "test",
            options = {"aspect_ratio": Fraction(3.0/4)}, 
            expected_url = DEFAULT_UPLOAD_PATH + "ar_3:4/test")

    def test_overlay_options(self):
        tests = [
            dict(public_id = "logo"),"logo",
            dict(public_id = "folder/logo"),"folder:logo",
            dict(public_id = "logo",type = "private"),"private:logo",
            dict(public_id = "logo",format = "png"),"logo.png",
            dict(resource_type = "video",public_id = "cat"),"video:cat",
            dict(text = "Hello World, Nice to meet you?", font_family = "Arial", font_size = "18"),"text:Arial_18:Hello%20World%E2%80%9A%20Nice%20to%20meet%20you%3F",
            dict(text = "Hello World, Nice to meet you?", font_family = "Arial", font_size = "18", font_weight = "bold", font_style = "italic", letter_spacing = 4, line_spacing = 3),"text:Arial_18_bold_italic_letter_spacing_4_line_spacing_3:Hello%20World%E2%80%9A%20Nice%20to%20meet%20you%3F",
            dict(resource_type = "subtitles",public_id = "sample_sub_en.srt"),"subtitles:sample_sub_en.srt",
            dict(resource_type = "subtitles",public_id = "sample_sub_he.srt", font_family = "Arial", font_size = 40),"subtitles:Arial_40:sample_sub_he.srt"
        ]

        for i in cldrange(0, len(tests), 2):
            options = tests[i]
            expected = tests[i + 1]
            result = cloudinary.utils.process_layer(options, "overlay")
            self.assertEqual(expected, result)

    def test_overlay_error_1(self):
        """ Must supply font_family for text in overlay """
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", overlay = dict(text = "text", font_style = "italic"))

    def test_overlay_error_2(self):
        """ Must supply public_id for for non-text underlay """
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", underlay = dict(resource_type = "video"))


    def test_translate_if(self):
        all_operators = "if_"
        all_operators += "w_eq_0_and" 
        all_operators += "_h_ne_0_or"
        all_operators += "_ar_lt_0_and"
        all_operators += "_pc_gt_0_and"
        all_operators += "_fc_lte_0_and"
        all_operators += "_w_gte_0"
        all_operators += ",e_grayscale"
        condition = "width = 0 && height != 0 || aspect_ratio < 0 && page_count > 0 and face_count <= 0 and width >= 0"
        options = {"if": condition, "effect": "grayscale"}
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertEqual({}, options)
        self.assertEqual(all_operators, transformation)

if __name__ == '__main__':
    unittest.main()
