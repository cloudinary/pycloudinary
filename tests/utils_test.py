import cloudinary.utils
import unittest

class TestUtils(unittest.TestCase):
    def setUp(self):
        cloudinary.config(cloud_name = "test123", secure_distribution = None, private_cdn = False)

    def test_cloud_name(self):
        """should use cloud_name from config"""
        result, options = cloudinary.utils.cloudinary_url("test")
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/test" )

    def test_cloud_name_options(self):
        """should allow overriding cloud_name in options"""
        options = {"cloud_name": "test321"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test321/image/upload/test" )

    def test_secure_distribution(self):
        """should use default secure distribution if secure=True"""
        options = {"secure": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "https://res.cloudinary.com/test123/image/upload/test" )

    def test_secure_distribution_overwrite(self):
        """should allow overwriting secure distribution if secure=True"""
        options = {"secure": True, "secure_distribution": "something.else.com"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "https://something.else.com/test123/image/upload/test" )

    def test_secure_distibution(self):
        """should take secure distribution from config if secure=True"""
        cloudinary.config().secure_distribution = "config.secure.distribution.com"
        options = {"secure": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "https://config.secure.distribution.com/test123/image/upload/test" )

    def test_secure_akamai(self):
        """should default to akamai if secure is given with private_cdn and no secure_distribution"""
        options = {"secure": True, "private_cdn": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "https://test123-res.cloudinary.com/image/upload/test" )

    def test_secure_non_akamai(self):
        """should not add cloud_name if private_cdn and secure non akamai secure_distribution"""
        options = {"secure": True, "private_cdn": True, "secure_distribution": "something.cloudfront.net"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "https://something.cloudfront.net/image/upload/test")

    def test_http_private_cdn(self):
        """should not add cloud_name if private_cdn and not secure"""
        options = {"private_cdn": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://test123-res.cloudinary.com/image/upload/test")

    def test_format(self):
        """should use format from options"""
        options = {"format": "jpg"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/test.jpg" )

    def test_crop(self):
        """should always use width and height from options"""
        options = {"width": 100, "height": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/h_100,w_100/test" )
        self.assertEqual(options, {"width": 100, "height": 100})
        options = {"width": 100, "height": 100, "crop": "crop"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": 100, "height": 100})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_crop,h_100,w_100/test" )

    def test_html_width_height_on_crop_fit_limit(self):
        """should not pass width and height to html in case of fit or limit crop"""
        options = {"width": 100, "height": 100, "crop": "limit"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_limit,h_100,w_100/test" )
        self.assertEqual(options, {})
        options = {"width": 100, "height": 100, "crop": "fit"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_fit,h_100,w_100/test" )

    def test_html_width_height_on_angle(self):
        """should not pass width and height to html in case angle was used"""
        options = {"width": 100, "height": 100, "crop": "scale", "angle": "auto"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/a_auto,c_scale,h_100,w_100/test" )
        self.assertEqual(options, {})

    def test_various_options(self):
        """should use x, y, radius, prefix, gravity and quality from options"""
        options = {"x": 1, "y": 2, "opacity": 20, "radius": 3, "gravity": "center", "quality": 0.4, "prefix": "a"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/g_center,o_20,p_a,q_0.4,r_3,x_1,y_2/test" )

    def test_transformation_simple(self):
        """should support named tranformation"""
        options = {"transformation": "blip"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/t_blip/test" )

    def test_transformation_array(self):
        """should support array of named tranformations"""
        options = {"transformation": ["blip", "blop"]}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/t_blip.blop/test" )

    def test_base_transformations(self):
        """should support base tranformation"""
        options = {"transformation": {"x": 100, "y": 100, "crop": "fill"}, "crop": "crop", "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": 100})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_fill,x_100,y_100/c_crop,w_100/test" )

    def test_base_transformation_array(self):
        """should support array of base tranformations"""
        options = {"transformation": [{"x": 100, "y": 100, "width": 200, "crop": "fill"}, {"radius": 10}], "crop": "crop", "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": 100})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_fill,w_200,x_100,y_100/r_10/c_crop,w_100/test" )

    def test_no_empty_transformation(self):
        """should not include empty tranformations"""
        options = {"transformation": [{}, {"x": 100, "y": 100, "crop": "fill"}, {}]}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_fill,x_100,y_100/test" )

    def test_size(self):
        """should support size"""
        options = {"size": "10x10", "crop": "crop"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": "10", "height": "10"})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/c_crop,h_10,w_10/test" )

    def test_type(self):
        """should use type from options"""
        options = {"type": "facebook"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/facebook/test" )

    def test_resource_type(self):
        """should use resource_type from options"""
        options = {"resource_type": "raw"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/raw/upload/test" )

    def test_ignore_http(self):
        """should ignore http links only if type is not given or is asset"""
        options = {}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://test" )
        options = {"type": "asset"}
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
        options = {"cname": "hello.com"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://hello.com/test123/image/upload/test" )

    def test_cname_subdomain(self):
        """should support extenal cname with cdn_subdomain on"""
        options = {"cname": "hello.com", "cdn_subdomain": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://a2.hello.com/test123/image/upload/test" )

    def test_background(self):
        """should support background"""
        options = {"background": "red"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/b_red/test" )
        options = {"background": "#112233"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/b_rgb:112233/test" )

    def test_default_image(self):
        """should support default_image"""
        options = {"default_image": "default"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/d_default/test" )

    def test_angle(self):
        """should support angle"""
        options = {"angle": 12}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/a_12/test" )

    def test_overlay(self):
        """should support overlay"""
        options = {"overlay": "text:hello"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/l_text:hello/test" )
        # Should not pass width height to HTML with overlay
        options = {"overlay": "text:hello", "height": 100, "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/h_100,l_text:hello,w_100/test" )

    def test_underlay(self):
        """should support underlay"""
        options = {"underlay": "text:hello"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/u_text:hello/test" )
        # Should not pass width height to HTML with underlay
        options = {"underlay": "text:hello", "height": 100, "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/h_100,u_text:hello,w_100/test" )

    def test_fetch_format(self):
        """should support format for fetch urls"""
        options = {"format": "jpg", "type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://cloudinary.com/images/logo.png", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/fetch/f_jpg/http://cloudinary.com/images/logo.png" )

    def test_effect(self):
        """should support effect"""
        options = {"effect": "sepia"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/e_sepia/test" )

    def test_effect_with_dict(self):
        """should support effect with dict"""
        options = {"effect": {"sepia": 10}}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/e_sepia:10/test" )

    def test_effect_with_array(self):
        """should support effect with array"""
        options = {"effect": ["sepia", 10]}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/e_sepia:10/test" )

    def test_density(self):
        """should support density"""
        options = {"density": 150}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/dn_150/test" )

    def test_page(self):
        """should support page"""
        options = {"page": 3}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/pg_3/test" )

    def test_border(self):
        """should support border"""
        options = {"border": {"width": 5}}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/bo_5px_solid_black/test" )
        options = {"border": {"width": 5, "color": "#ffaabbdd"}}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/bo_5px_solid_rgb:ffaabbdd/test" )
        options = {"border": "1px_solid_blue"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/bo_1px_solid_blue/test" )

    def test_flags(self):
        """should support flags"""
        options = {"flags": "abc"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/fl_abc/test" )
        options = {"flags": ["abc", "def"]}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/fl_abc.def/test" )

    def test_folder_version(self):
        """should add version if public_id contains / """
        result, options = cloudinary.utils.cloudinary_url("folder/test")
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/v1/folder/test")
        result, options = cloudinary.utils.cloudinary_url("folder/test", version=123)
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/v123/folder/test")
        result, options = cloudinary.utils.cloudinary_url("v1234/test")
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/upload/v1234/test")

    def test_shorten(self):
        result, options = cloudinary.utils.cloudinary_url("test", shorten=True)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/iu/test")

        result, options = cloudinary.utils.cloudinary_url("test", shorten=True, type="private")
        self.assertEqual(options, {})
        self.assertEqual(result, "http://res.cloudinary.com/test123/image/private/test")
    
    def test_escape_public_id(self):
        """ should escape public_ids """
        tests = {
            "a b": "a%20b",
            "a+b": "a%2Bb",
            "a%20b": "a%20b",
            "a-b": "a-b",
            "a??b": "a%3F%3Fb"};
        for source, target in tests.items():
            result, options = cloudinary.utils.cloudinary_url(source)
            self.assertEquals("http://res.cloudinary.com/test123/image/upload/" + target, result)

if __name__ == '__main__':
    unittest.main()
