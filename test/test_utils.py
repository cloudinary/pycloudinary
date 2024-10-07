# -*- coding: utf-8 -*-
import io
import re
import tempfile
import unittest
import uuid
import time
from collections import OrderedDict
from datetime import datetime, date
from fractions import Fraction
from os.path import getsize

import six

import cloudinary.utils
from cloudinary import CL_BLANK
from cloudinary.utils import (
    api_sign_request,
    build_list_of_dicts,
    json_encode,
    encode_unicode_url,
    base64url_encode,
    patch_fetch_format,
    cloudinary_scaled_url,
    chain_transformations,
    generate_transformation_string,
    build_eager,
    compute_hex_hash,
    verify_notification_signature,
    verify_api_response_signature,
)
from cloudinary.compat import to_bytes
from test.helper_test import TEST_IMAGE, REMOTE_TEST_IMAGE, patch
from test.test_api import (
    API_TEST_TRANS_SCALE100,
    API_TEST_TRANS_SCALE100_STR,
    API_TEST_TRANS_SEPIA_STR,
    API_TEST_TRANS_SEPIA
)

DEFAULT_ROOT_PATH = 'http://res.cloudinary.com/test123/'

DEFAULT_UPLOAD_PATH = DEFAULT_ROOT_PATH + 'image/upload/'
DEFAULT_FETCH_PATH = DEFAULT_ROOT_PATH + 'image/fetch/'
VIDEO_UPLOAD_PATH = DEFAULT_ROOT_PATH + 'video/upload/'
TEST_ID = 'test'

FETCH_URL = "https://cloudinary.com/images/logo.png"
FETCH_VIDEO_URL = "https://demo-res.cloudinary.com/videos/dog.mp4"

IMAGE_VERSION = "1234"
IMAGE_VERSION_STR = "v" + IMAGE_VERSION
DEFAULT_VERSION_STR = 'v1'
TEST_FOLDER = 'folder/test'

MOCKED_NOW = 1549533574
API_SECRET = 'X7qLTrsES31MzxxkxPPA-pAGGfU'


class TestUtils(unittest.TestCase):
    crop_transformation = {'crop': 'crop', 'width': 100}
    crop_transformation_str = 'c_crop,w_100'
    raw_transformation = "c_fill,e_grayscale,q_auto"

    custom_function_wasm = {"function_type": "wasm", "source": "blur.wasm"}
    custom_function_wasm_str = "wasm:blur.wasm"

    custom_function_remote = {
        "function_type": "remote",
        "source": "https://df34ra4a.execute-api.us-west-2.amazonaws.com/default/cloudinaryFn"}
    custom_function_remote_str = \
        "remote:aHR0cHM6Ly9kZjM0cmE0YS5leGVjdXRlLWFwaS51cy13ZXN0LTIuYW1hem9uYXdzLmNvbS9kZWZhdWx0L2Nsb3VkaW5hcnlGbg=="

    def setUp(self):
        cloudinary.config(cloud_name="test123",
                          cname=None,  # for these tests without actual upload, we ignore cname
                          api_key="a", api_secret="b",
                          secure_distribution=None,
                          private_cdn=False)

    def __test_cloudinary_url(self, public_id=TEST_ID, options=None, expected_url=None, expected_options=None):
        if expected_options is None:
            expected_options = {}
        if options is None:
            options = {}
        url, options = cloudinary.utils.cloudinary_url(public_id, **options)
        self.assertEqual(expected_url, url)
        self.assertEqual(expected_options, options)

    def test_cloud_name(self):
        """should use cloud_name from config"""
        self.__test_cloudinary_url(options={}, expected_url=DEFAULT_UPLOAD_PATH + "test")

    def test_cloud_name_options(self):
        """should allow overriding cloud_name in options"""
        self.__test_cloudinary_url(options={"cloud_name": "test321"},
                                   expected_url="http://res.cloudinary.com/test321/image/upload/test")

    def test_secure_distribution(self):
        """should use default secure distribution if secure=True"""
        self.__test_cloudinary_url(options={"secure": True},
                                   expected_url="https://res.cloudinary.com/test123/image/upload/test")

    def test_secure_distribution_overwrite(self):
        """should allow overwriting secure distribution if secure=True"""
        self.__test_cloudinary_url(options={"secure": True, "secure_distribution": "something.else.com"},
                                   expected_url="https://something.else.com/test123/image/upload/test")

    def test_secure_distibution(self):
        """should take secure distribution from config if secure=True"""
        cloudinary.config().secure_distribution = "config.secure.distribution.com"
        self.__test_cloudinary_url(options={"secure": True},
                                   expected_url="https://config.secure.distribution.com/test123/image/upload/test")

    def test_secure_akamai(self):
        """should default to akamai if secure is given with private_cdn and no secure_distribution"""
        self.__test_cloudinary_url(options={"secure": True, "private_cdn": True},
                                   expected_url="https://test123-res.cloudinary.com/image/upload/test")

    def test_secure_non_akamai(self):
        """should not add cloud_name if private_cdn and secure non akamai secure_distribution"""
        self.__test_cloudinary_url(
            options={"secure": True, "private_cdn": True, "secure_distribution": "something.cloudfront.net"},
            expected_url="https://something.cloudfront.net/image/upload/test")

    def test_http_private_cdn(self):
        """should not add cloud_name if private_cdn and not secure"""
        self.__test_cloudinary_url(options={"private_cdn": True},
                                   expected_url="http://test123-res.cloudinary.com/image/upload/test")

    def test_format(self):
        """should use format from options"""
        self.__test_cloudinary_url(options={"format": "jpg"}, expected_url=DEFAULT_UPLOAD_PATH + "test.jpg")

    def test_crop(self):
        """should always use width and height from options"""
        self.__test_cloudinary_url(
            options={"width": 100, "height": 100},
            expected_url=DEFAULT_UPLOAD_PATH + "h_100,w_100/test",
            expected_options={"width": 100, "height": 100})
        self.__test_cloudinary_url(
            options={"width": 100, "height": 100, "crop": "crop"},
            expected_url=DEFAULT_UPLOAD_PATH + "c_crop,h_100,w_100/test",
            expected_options={"width": 100, "height": 100})

    def test_html_width_height_on_crop_fit_limit(self):
        """should not pass width and height to html in case of fit or limit crop"""
        self.__test_cloudinary_url(options={"width": 100, "height": 100, "crop": "limit"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_limit,h_100,w_100/test")
        self.__test_cloudinary_url(options={"width": 100, "height": 100, "crop": "fit"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fit,h_100,w_100/test")

    def test_html_width_height_on_angle(self):
        """should not pass width and height to html in case angle was used"""
        self.__test_cloudinary_url(options={"width": 100, "height": 100, "crop": "scale", "angle": "auto"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "a_auto,c_scale,h_100,w_100/test")

    def test_various_options(self):
        """should use x, y, radius, prefix, gravity and quality from options"""
        self.__test_cloudinary_url(
            options={"x": 1, "y": 2, "opacity": 20, "radius": 3, "gravity": "center", "quality": 0.4, "prefix": "a"},
            expected_url=DEFAULT_UPLOAD_PATH + "g_center,o_20,p_a,q_0.4,r_3,x_1,y_2/test")
        self.__test_cloudinary_url(options={"gravity": "auto", "width": 0.5, "crop": "crop"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_crop,g_auto,w_0.5/test")

    def test_radius(self):
        cases = (
            ({"radius": 10}, "r_10"),
            ({"radius": "10"}, "r_10"),
            ({"radius": "$v", "variables": [("$v", 10)]}, "$v_10,r_$v"),
            ({"radius": "width * 2"}, "r_w_mul_2"),
            ({"radius": [10, 20]}, "r_10:20"),
            ({"radius": "10:20"}, "r_10:20"),
            ({"radius": "10:$v", "variables": [("$v", 20)]}, "$v_20,r_10:$v"),
            ({"radius": [10, 20, 30]}, "r_10:20:30"),
            ({"radius": "10:20:30"}, "r_10:20:30"),
            ({"radius": "10:$v:30", "variables": [("$v", 20)]}, "$v_20,r_10:$v:30"),
            ({"radius": [10, 20, 30, 40]}, "r_10:20:30:40"),
            ({"radius": "10:20:30:40"}, "r_10:20:30:40"),
            ({"radius": "10:$v:30:40", "variables": [("$v", 20)]}, "$v_20,r_10:$v:30:40"),
        )
        for options, expected_part_url in cases:
            self.__test_cloudinary_url(options=options, expected_url=DEFAULT_UPLOAD_PATH + expected_part_url + "/test")

        wrong_options = (
            {"radius": []},
            {"radius": ()},
            {"radius": [10, 20, 30, 40, 50]},
        )
        for options in wrong_options:
            with self.assertRaises(ValueError):
                cloudinary.utils.cloudinary_url("test", **options)

    def test_should_support_auto_width(self):
        """should support auto width"""
        self.__test_cloudinary_url(options={"width": "auto:20", "crop": 'fill'},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fill,w_auto:20/test",
                                   expected_options={'responsive': True})
        self.__test_cloudinary_url(options={"width": "auto:20:350", "crop": 'fill'},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fill,w_auto:20:350/test",
                                   expected_options={'responsive': True})
        self.__test_cloudinary_url(options={"width": "auto:breakpoints", "crop": 'fill'},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fill,w_auto:breakpoints/test",
                                   expected_options={'responsive': True})
        self.__test_cloudinary_url(options={"width": "auto:breakpoints_100_1900_20_15", "crop": 'fill'},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fill,w_auto:breakpoints_100_1900_20_15/test",
                                   expected_options={'responsive': True})
        self.__test_cloudinary_url(options={"width": "auto:breakpoints:json", "crop": 'fill'},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fill,w_auto:breakpoints:json/test",
                                   expected_options={'responsive': True})

    def test_original_width_and_height(self):
        """should support original width and height"""
        self.__test_cloudinary_url(options={"crop": "crop", "width": "ow", "height": "oh"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_crop,h_oh,w_ow/test")

    def test_support_a_percent_value(self):
        """quality support a percent value"""
        self.__test_cloudinary_url(
            options={"x": 1, "y": 2, "radius": 3, "gravity": "center", "quality": 80, "prefix": "a"},
            expected_url=DEFAULT_UPLOAD_PATH + "g_center,p_a,q_80,r_3,x_1,y_2/test")
        self.__test_cloudinary_url(
            options={"x": 1, "y": 2, "radius": 3, "gravity": "center", "quality": "80:444", "prefix": "a"},
            expected_url=DEFAULT_UPLOAD_PATH + "g_center,p_a,q_80:444,r_3,x_1,y_2/test")

    def test_should_support_auto_value(self):
        """quality should support auto value"""
        self.__test_cloudinary_url(
            options={"x": 1, "y": 2, "radius": 3, "gravity": "center", "quality": "auto", "prefix": "a"},
            expected_url=DEFAULT_UPLOAD_PATH + "g_center,p_a,q_auto,r_3,x_1,y_2/test")
        self.__test_cloudinary_url(
            options={"x": 1, "y": 2, "radius": 3, "gravity": "center", "quality": "auto:good", "prefix": "a"},
            expected_url=DEFAULT_UPLOAD_PATH + "g_center,p_a,q_auto:good,r_3,x_1,y_2/test")
        self.__test_cloudinary_url(
            options={"width": 100, "height": 100, "crop": 'crop', "gravity": "auto:ocr_text"},
            expected_url=DEFAULT_UPLOAD_PATH + "c_crop,g_auto:ocr_text,h_100,w_100/test",
            expected_options={"width": 100, "height": 100})
        self.__test_cloudinary_url(
            options={"width": 100, "height": 100, "crop": 'crop', "gravity": "ocr_text"},
            expected_url=DEFAULT_UPLOAD_PATH + "c_crop,g_ocr_text,h_100,w_100/test",
            expected_options={"width": 100, "height": 100})
        self.__test_cloudinary_url(
            options={"width": 100, "height": 100, "crop": 'crop', "gravity": "ocr_text:adv_ocr"},
            expected_url=DEFAULT_UPLOAD_PATH + "c_crop,g_ocr_text:adv_ocr,h_100,w_100/test",
            expected_options={"width": 100, "height": 100})

    def test_transformation_simple(self):
        """should support named transformation"""
        self.__test_cloudinary_url(options={"transformation": "blip"}, expected_url=DEFAULT_UPLOAD_PATH + "t_blip/test")

    def test_transformation_array(self):
        """should support array of named transformations"""
        self.__test_cloudinary_url(options={"transformation": ["blip", "blop"]},
                                   expected_url=DEFAULT_UPLOAD_PATH + "t_blip.blop/test")

    def test_base_transformations(self):
        """should support base transformation"""
        self.__test_cloudinary_url(
            options={"transformation": {"x": 100, "y": 100, "crop": "fill"}, "crop": "crop", "width": 100},
            expected_url=DEFAULT_UPLOAD_PATH + "c_fill,x_100,y_100/c_crop,w_100/test",
            expected_options={"width": 100})

    def test_base_transformation_array(self):
        """should support array of base transformations"""
        options = {"transformation": [{"x": 100, "y": 100, "width": 200, "crop": "fill"}, {"radius": 10}],
                   "crop": "crop", "width": 100}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": 100})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_fill,w_200,x_100,y_100/r_10/c_crop,w_100/test")

    def test_no_empty_transformation(self):
        """should not include empty transformations"""
        self.__test_cloudinary_url(options={"transformation": [{}, {"x": 100, "y": 100, "crop": "fill"}, {}]},
                                   expected_url=DEFAULT_UPLOAD_PATH + "c_fill,x_100,y_100/test")

    def test_raw_transformation(self):
        """should include raw_transformation"""
        self.__test_cloudinary_url(options={"transformation": {"width": 100, "raw_transformation": "g_north_west"}},
                                   expected_url=DEFAULT_UPLOAD_PATH + "w_100,g_north_west/test")
        self.__test_cloudinary_url(options={"transformation": {"raw_transformation": "g_north_west"}},
                                   expected_url=DEFAULT_UPLOAD_PATH + "g_north_west/test")
        self.__test_cloudinary_url(options={"transformation": {"width": 100, "raw_transformation": ""}},
                                   expected_url=DEFAULT_UPLOAD_PATH + "w_100/test")

    def test_chain_transformations(self):
        """Should support chaining transformations at the end"""
        options = {"effect": "art:incognito", "format": "png"}
        chained_transformations = [
            {"x": 100, "y": 100, "width": 200, "crop": "fill"},
            {"radius": 10},
            {"raw_transformation": self.raw_transformation}
        ]

        actual_options = chain_transformations(options, chained_transformations)
        actual_transformation_str = generate_transformation_string(**actual_options)[0]

        self.assertEqual("e_art:incognito/c_fill,w_200,x_100,y_100/r_10/" + self.raw_transformation,
                         actual_transformation_str)

        # Should support chaining transformations, when default options have no transformations
        actual_options = chain_transformations({}, chained_transformations)
        actual_transformation_str = generate_transformation_string(**actual_options)[0]

        self.assertEqual("c_fill,w_200,x_100,y_100/r_10/" + self.raw_transformation,
                         actual_transformation_str)

        # Should handle  empty list of chained transformations

        actual_options = chain_transformations(options, [])
        actual_transformation_str = generate_transformation_string(**actual_options)[0]
        self.assertEqual("e_art:incognito", actual_transformation_str)

        # Should handle empty options and empty list of chained transformations

        actual_options = chain_transformations({}, [])
        actual_transformation_str = generate_transformation_string(**actual_options)[0]

        self.assertEqual("", actual_transformation_str)

        # Should remove transformation options from resulting options
        actual_options = chain_transformations(dict(width=200, height=100), chained_transformations)

        self.assertNotIn("width", actual_options)
        self.assertNotIn("height", actual_options)

        actual_transformation_str = generate_transformation_string(**actual_options)[0]

        self.assertEqual("h_100,w_200/c_fill,w_200,x_100,y_100/r_10/c_fill,e_grayscale,q_auto",
                         actual_transformation_str)

        # Should chain transformations with a fetch option
        options["type"] = "fetch"

        patch_fetch_format(options)
        actual_options = chain_transformations(options, chained_transformations)

        # format should be removed when we use fetch
        self.assertNotIn("format", actual_options)

        actual_transformation_str = generate_transformation_string(**actual_options)[0]

        # Should use url format as a fetch_format
        self.assertEqual("e_art:incognito,f_png/c_fill,w_200,x_100,y_100/r_10/" + self.raw_transformation,
                         actual_transformation_str)

        options["fetch_format"] = "gif"

        actual_options = chain_transformations(options, chained_transformations)
        actual_transformation_str = generate_transformation_string(**actual_options)[0]

        # Should use fetch_format
        self.assertEqual("e_art:incognito,f_gif/c_fill,w_200,x_100,y_100/r_10/" + self.raw_transformation,
                         actual_transformation_str)

    def test_size(self):
        """should support size"""
        options = {"size": "10x10", "crop": "crop"}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"width": "10", "height": "10"})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_crop,h_10,w_10/test")

    def test_type(self):
        """should use type from options"""
        self.__test_cloudinary_url(options={"type": "facebook"}, expected_url=DEFAULT_ROOT_PATH + "image/facebook/test")

    def test_resource_type(self):
        """should use resource_type from options"""
        self.__test_cloudinary_url(options={"resource_type": "raw"}, expected_url=DEFAULT_ROOT_PATH + "raw/upload/test")

    def test_ignore_http(self):
        """should ignore http links only if type is not given or is asset"""
        options = {}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, "http://test")
        options = {"type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://test", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, DEFAULT_ROOT_PATH + "image/fetch/http://test")

    def test_fetch(self):
        """should escape fetch urls"""
        options = {"type": "fetch"}
        result, options = cloudinary.utils.cloudinary_url("http://blah.com/hello?a=b", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, DEFAULT_ROOT_PATH + "image/fetch/http://blah.com/hello%3Fa%3Db")

    def test_http_escape(self):
        """should escape http urls"""
        options = {"type": "youtube"}
        result, options = cloudinary.utils.cloudinary_url("http://www.youtube.com/watch?v=d9NF2edxy-M", **options)
        self.assertEqual(options, {})
        self.assertEqual(result, DEFAULT_ROOT_PATH + "image/youtube/http://www.youtube.com/watch%3Fv%3Dd9NF2edxy-M")

    def test_cname(self):
        """should support extenal cname"""
        self.__test_cloudinary_url(options={"cname": "hello.com"},
                                   expected_url="http://hello.com/test123/image/upload/test")

    def test_cname_subdomain(self):
        """should support extenal cname with cdn_subdomain on"""
        self.__test_cloudinary_url(options={"cname": "hello.com", "cdn_subdomain": True},
                                   expected_url="http://a2.hello.com/test123/image/upload/test")

    def test_background(self):
        """should support background"""
        self.__test_cloudinary_url(options={"background": "red"}, expected_url=DEFAULT_UPLOAD_PATH + "b_red/test")
        self.__test_cloudinary_url(options={"background": "#112233"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "b_rgb:112233/test")

    def test_default_image(self):
        """should support default_image"""
        self.__test_cloudinary_url(options={"default_image": "default"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "d_default/test")

    def test_angle(self):
        """should support angle"""
        self.__test_cloudinary_url(options={"angle": 12}, expected_url=DEFAULT_UPLOAD_PATH + "a_12/test")

    def test_overlay(self):
        """should support overlay"""
        self.__test_cloudinary_url(options={"overlay": "text:hello"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "l_text:hello/test")
        # Should not pass width height to HTML with overlay
        self.__test_cloudinary_url(options={"overlay": "text:hello", "height": 100, "width": 100},
                                   expected_url=DEFAULT_UPLOAD_PATH + "h_100,l_text:hello,w_100/test")

        self.__test_cloudinary_url(
            options={"overlay": {"font_family": "arial", "font_size": 20, "text": "hello"}, "height": 100,
                     "width": 100}, expected_url=DEFAULT_UPLOAD_PATH + "h_100,l_text:arial_20:hello,w_100/test")

    def test_fetch_overlay(self):
        """should support overlay"""
        self.__test_cloudinary_url(
            options={"overlay": "fetch:" + REMOTE_TEST_IMAGE},
            expected_url=(
                    DEFAULT_UPLOAD_PATH
                    + "l_fetch:aHR0cDovL2Nsb3VkaW5hcnkuY29tL2ltYWdlcy9vbGRfbG9nby5wbmc=/"
                    + "test"))

        """should support video overlay"""
        self.__test_cloudinary_url(
            options={"overlay": "video:fetch:" + FETCH_VIDEO_URL},
            expected_url=(
                    DEFAULT_UPLOAD_PATH
                    + "l_video:fetch:aHR0cHM6Ly9kZW1vLXJlcy5jbG91ZGluYXJ5LmNvbS92aWRlb3MvZG9nLm1wNA==/"
                    + "test"))

        self.__test_cloudinary_url(
            options={
                "overlay": {
                    "url":
                        "https://upload.wikimedia.org/wikipedia/commons/2/2b/고창갯벌.jpg"}},
            expected_url=(
                    DEFAULT_UPLOAD_PATH +
                    "l_fetch:"
                    "aHR0cHM6Ly91cGxvYWQud2lraW1lZGlhLm9yZy93aWtpcGVkaWEvY29tbW9ucy8yLzJiL-qzoOywveqwr-uyjC5qcGc=/"
                    "test"))

        self.__test_cloudinary_url(
            options={
                "overlay": {
                    "url":
                        "https://www.test.com/test/JE01118-YGP900_1_lar.jpg?version=432023"}},
            expected_url=(
                    DEFAULT_UPLOAD_PATH +
                    "l_fetch:"
                    "aHR0cHM6Ly93d3cudGVzdC5jb20vdGVzdC9KRTAxMTE4LVlHUDkwMF8xX2xhci5qcGc_dmVyc2lvbj00MzIwMjM=/"
                    "test"))

    def test_underlay(self):
        """should support underlay"""
        self.__test_cloudinary_url(options={"underlay": "text:hello"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "u_text:hello/test")
        # Should not pass width height to HTML with underlay
        self.__test_cloudinary_url(options={"underlay": "text:hello", "height": 100, "width": 100},
                                   expected_url=DEFAULT_UPLOAD_PATH + "h_100,u_text:hello,w_100/test")

    def test_custom_function(self):

        # should support custom function from string
        options = {"custom_function": self.custom_function_wasm_str}
        self.__test_cloudinary_url(
            options=options,
            expected_url=DEFAULT_UPLOAD_PATH + "fn_" + self.custom_function_wasm_str + "/test"
        )

        # should support custom function from dictionary
        options = {"custom_function": self.custom_function_wasm}
        self.__test_cloudinary_url(
            options=options,
            expected_url=DEFAULT_UPLOAD_PATH + "fn_" + self.custom_function_wasm_str + "/test"
        )
        # should encode custom function source for remote function
        options = {"custom_function": self.custom_function_remote}
        self.__test_cloudinary_url(
            options=options,
            expected_url=DEFAULT_UPLOAD_PATH + "fn_" + self.custom_function_remote_str + "/test"
        )

    def test_custom_pre_function_wasm_str(self):
        # should support custom pre function from string
        options = {"custom_pre_function": self.custom_function_wasm_str}
        self.__test_cloudinary_url(
            options=options,
            expected_url=DEFAULT_UPLOAD_PATH + "fn_pre:" + self.custom_function_wasm_str + "/test"
        )

    def test_custom_pre_function_wasm_dictionary(self):
        # should support custom pre function from dictionary
        options = {"custom_pre_function": self.custom_function_wasm}
        self.__test_cloudinary_url(
            options=options,
            expected_url=DEFAULT_UPLOAD_PATH + "fn_pre:" + self.custom_function_wasm_str + "/test"
        )

    def test_custom_pre_function_remote(self):
        # should encode custom function source for remote function
        options = {"custom_pre_function": self.custom_function_remote}
        self.__test_cloudinary_url(
            options=options,
            expected_url=DEFAULT_UPLOAD_PATH + "fn_pre:" + self.custom_function_remote_str + "/test"
        )

    def test_fetch_format(self):
        """should support format for fetch urls"""
        self.__test_cloudinary_url(
            public_id="http://cloudinary.com/images/logo.png",
            options={"format": "jpg", "type": "fetch"},
            expected_url=DEFAULT_ROOT_PATH + "image/fetch/f_jpg/http://cloudinary.com/images/logo.png"
        )

    def test_effect(self):
        """should support effect"""
        self.__test_cloudinary_url(options={"effect": "sepia"}, expected_url=DEFAULT_UPLOAD_PATH + "e_sepia/test")

    def test_effect_with_dict(self):
        """should support effect with dict"""
        self.__test_cloudinary_url(options={"effect": {"sepia": -10}},
                                   expected_url=DEFAULT_UPLOAD_PATH + "e_sepia:-10/test")

    def test_effect_with_array(self):
        """should support effect with array"""
        self.__test_cloudinary_url(options={"effect": ["sepia", 10]},
                                   expected_url=DEFAULT_UPLOAD_PATH + "e_sepia:10/test")

    def test_keyframe_interval(self):
        """should support keyframe_interval"""
        test_values = (
            (10, "ki_10.0"),
            (0.05, "ki_0.05"),
            (3.45, "ki_3.45"),
            (300, "ki_300.0"),
            ("10", "ki_10"),
        )
        for value, expected in test_values:
            self.__test_cloudinary_url(options={"resource_type": "video", "keyframe_interval": value},
                                       expected_url=VIDEO_UPLOAD_PATH + expected + "/test")
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", keyframe_interval=-1)

    def test_streaming_profile(self):
        """should support streaming_profile"""
        self.__test_cloudinary_url(options={"streaming_profile": "some-profile"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "sp_some-profile/test")

    def test_density(self):
        """should support density"""
        self.__test_cloudinary_url(options={"density": 150}, expected_url=DEFAULT_UPLOAD_PATH + "dn_150/test")

    def test_page(self):
        """should support page"""
        self.__test_cloudinary_url(options={"page": 3}, expected_url=DEFAULT_UPLOAD_PATH + "pg_3/test")

    def test_border(self):
        """should support border"""
        self.__test_cloudinary_url(options={"border": {"width": 5}},
                                   expected_url=DEFAULT_UPLOAD_PATH + "bo_5px_solid_black/test")
        self.__test_cloudinary_url(options={"border": {"width": 5, "color": "#ffaabbdd"}},
                                   expected_url=DEFAULT_UPLOAD_PATH + "bo_5px_solid_rgb:ffaabbdd/test")
        self.__test_cloudinary_url(options={"border": "1px_solid_blue"},
                                   expected_url=DEFAULT_UPLOAD_PATH + "bo_1px_solid_blue/test")

    def test_flags(self):
        """should support flags"""
        self.__test_cloudinary_url(options={"flags": "abc"}, expected_url=DEFAULT_UPLOAD_PATH + "fl_abc/test")
        self.__test_cloudinary_url(options={"flags": ["abc", "def"]},
                                   expected_url=DEFAULT_UPLOAD_PATH + "fl_abc.def/test")

    def test_dpr(self):
        """should support dpr (device pixel radio)"""
        self.__test_cloudinary_url(options={"dpr": "2.0"}, expected_url=DEFAULT_UPLOAD_PATH + "dpr_2.0/test")

    def test_folder_version(self):
        """should add version if public_id contains / """
        self.__test_cloudinary_url(public_id="folder/test", expected_url=DEFAULT_UPLOAD_PATH + "v1/folder/test")
        self.__test_cloudinary_url(public_id="folder/test", options={"version": 123},
                                   expected_url=DEFAULT_UPLOAD_PATH + "v123/folder/test")
        self.__test_cloudinary_url(public_id="v1234/test", expected_url=DEFAULT_UPLOAD_PATH + "v1234/test")

    def test_force_version(self):
        """Should not set default version v1 to resources stored in folders if force_version is set to False"""
        self.__test_cloudinary_url(TEST_FOLDER,
                                   expected_url=DEFAULT_UPLOAD_PATH + DEFAULT_VERSION_STR + "/" + TEST_FOLDER)

        self.__test_cloudinary_url(TEST_FOLDER,
                                   options={"force_version": False},
                                   expected_url=DEFAULT_UPLOAD_PATH + TEST_FOLDER)

        # Explicitly set version is always passed
        self.__test_cloudinary_url(TEST_ID,
                                   options={"force_version": False, "version": IMAGE_VERSION},
                                   expected_url=DEFAULT_UPLOAD_PATH + IMAGE_VERSION_STR + "/" + TEST_ID)

        self.__test_cloudinary_url(TEST_FOLDER,
                                   options={"force_version": False, "version": IMAGE_VERSION},
                                   expected_url=DEFAULT_UPLOAD_PATH + IMAGE_VERSION_STR + "/" + TEST_FOLDER)

        # Should use force_version from config
        cloudinary.config(force_version=False)

        self.__test_cloudinary_url(TEST_FOLDER, expected_url=DEFAULT_UPLOAD_PATH + TEST_FOLDER)

        # Should override config with options
        self.__test_cloudinary_url(TEST_FOLDER,
                                   options={"force_version": True},
                                   expected_url=DEFAULT_UPLOAD_PATH + DEFAULT_VERSION_STR + "/" + TEST_FOLDER)

    def test_shorten(self):
        self.__test_cloudinary_url(options={"shorten": True}, expected_url=DEFAULT_ROOT_PATH + "iu/test")
        self.__test_cloudinary_url(options={"shorten": True, "type": "private"},
                                   expected_url=DEFAULT_ROOT_PATH + "image/private/test")

    def test_signed_url(self):
        self.__test_cloudinary_url(
            public_id="image.jpg",
            options={"version": 1234, "transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True},
            expected_url=DEFAULT_UPLOAD_PATH + "s--Ai4Znfl3--/c_crop,h_20,w_10/v1234/image.jpg")

        self.__test_cloudinary_url(
            public_id="image.jpg",
            options={"version": 1234, "sign_url": True},
            expected_url=DEFAULT_UPLOAD_PATH + "s----SjmNDA--/v1234/image.jpg")

        self.__test_cloudinary_url(
            public_id="image.jpg",
            options={"transformation": {"crop": "crop", "width": 10, "height": 20}, "sign_url": True},
            expected_url=DEFAULT_UPLOAD_PATH + "s--Ai4Znfl3--/c_crop,h_20,w_10/image.jpg")

        self.__test_cloudinary_url(
            public_id="image.jpg",
            options={"type": "authenticated", "transformation": {"crop": "crop", "width": 10, "height": 20},
                     "sign_url": True},
            expected_url=DEFAULT_ROOT_PATH + "image/authenticated/s--Ai4Znfl3--/c_crop,h_20,w_10/image.jpg")

        self.__test_cloudinary_url(
            public_id="http://google.com/path/to/image.png",
            options={"version": 1234, "type": "fetch", "sign_url": True},
            expected_url=DEFAULT_ROOT_PATH + "image/fetch/s--hH_YcbiS--/v1234/http://google.com/path/to/image.png")

        self.__test_cloudinary_url(
            public_id="image.jpg",
            options={"type": "authenticated", "transformation": {"color": "red", "overlay": {"text": "Cool%F0%9F%98%8D", "font_family": "Times", "font_size": 70, "font_weight": "bold"}},
                     "sign_url": True},
            expected_url="http://res.cloudinary.com/test123/image/authenticated/s--Uqk1a-5W--/co_red,l_text:Times_70_bold:Cool%25F0%259F%2598%258D/image.jpg")

        self.__test_cloudinary_url(
            public_id="image.jpg",
            options={"type": "authenticated", "transformation": {"raw_transformation": "co_red,l_text:Times_70_bold:Cool%25F0%259F%2598%258D"},
                     "sign_url": True},
            expected_url="http://res.cloudinary.com/test123/image/authenticated/s--Uqk1a-5W--/co_red,l_text:Times_70_bold:Cool%25F0%259F%2598%258D/image.jpg")

    def test_signed_url_sha256(self):
        sha256_config = cloudinary.Config()
        sha256_config.update(**vars(cloudinary.config()))
        sha256_config.update(signature_algorithm=cloudinary.utils.SIGNATURE_SHA256)
        with patch('cloudinary.config', return_value=sha256_config):
            self.__test_cloudinary_url(
                public_id="sample.jpg",
                options={"sign_url": True},
                expected_url=DEFAULT_UPLOAD_PATH + "s--2hbrSMPO--/sample.jpg")

    def test_disallow_url_suffix_in_non_upload_types(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix="hello", private_cdn=True, type="facebook")

    def test_disallow_url_suffix_with_slash_or_dot(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix="hello/world", private_cdn=True)
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", url_suffix="hello.world", private_cdn=True)

    def test_support_url_suffix_for_private_cdn(self):
        self.__test_cloudinary_url(options={"url_suffix": "hello", "private_cdn": True},
                                   expected_url="http://test123-res.cloudinary.com/images/test/hello")
        self.__test_cloudinary_url(options={"url_suffix": "hello", "angle": 0, "private_cdn": True},
                                   expected_url="http://test123-res.cloudinary.com/images/a_0/test/hello")

    def test_put_format_after_url_suffix(self):
        self.__test_cloudinary_url(options={"url_suffix": "hello", "private_cdn": True, "format": "jpg"},
                                   expected_url="http://test123-res.cloudinary.com/images/test/hello.jpg")

    def test_not_sign_the_url_suffix(self):
        url, options = cloudinary.utils.cloudinary_url("test", format="jpg", sign_url=True)
        expected_signature = re.search(r's--[0-9A-Za-z_-]{8}--', url)
        self.__test_cloudinary_url(
            options={"url_suffix": "hello", "private_cdn": True, "format": "jpg", "sign_url": True},
            expected_url="http://test123-res.cloudinary.com/images/" + expected_signature.group(0) + "/test/hello.jpg")

        url, options = cloudinary.utils.cloudinary_url("test", format="jpg", angle=0, sign_url=True)
        expected_signature = re.search(r's--[0-9A-Za-z_-]{8}--', url)
        self.__test_cloudinary_url(
            options={"url_suffix": "hello", "private_cdn": True, "format": "jpg", "angle": 0, "sign_url": True},
            expected_url="http://test123-res.cloudinary.com/images/" + expected_signature.group(
                0) + "/a_0/test/hello.jpg")

    def test_support_url_suffix_for_raw_uploads(self):
        self.__test_cloudinary_url(options={"url_suffix": "hello", "private_cdn": True, "resource_type": "raw"},
                                   expected_url="http://test123-res.cloudinary.com/files/test/hello")

    def test_support_use_root_path_for_shared_cdn(self):
        self.__test_cloudinary_url(options={"use_root_path": True, "private_cdn": False},
                                   expected_url=DEFAULT_ROOT_PATH + "test")
        self.__test_cloudinary_url(options={"use_root_path": True, "private_cdn": False, "angle": 0},
                                   expected_url=DEFAULT_ROOT_PATH + "a_0/test")

    def test_support_use_root_path_for_private_cdn(self):
        self.__test_cloudinary_url(options={"use_root_path": True, "private_cdn": True},
                                   expected_url="http://test123-res.cloudinary.com/test")
        self.__test_cloudinary_url(options={"use_root_path": True, "private_cdn": True, "angle": 0},
                                   expected_url="http://test123-res.cloudinary.com/a_0/test")

    def test_support_use_root_path_together_with_url_suffix_for_private_cdn(self):
        self.__test_cloudinary_url(options={"use_root_path": True, "url_suffix": "hello", "private_cdn": True},
                                   expected_url="http://test123-res.cloudinary.com/test/hello")

    def test_disallow_use_root_path_if_not_image_upload(self):
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", use_root_path=True, private_cdn=True, type="facebook")
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", use_root_path=True, private_cdn=True, resource_type="raw")

    def test_support_cdn_subdomain_with_secure_on_if_using_shared_domain(self):
        self.__test_cloudinary_url(options={"secure": True, "cdn_subdomain": True},
                                   expected_url="https://res-2.cloudinary.com/test123/image/upload/test")

    def test_support_secure_cdn_subdomain_false_override_with_secure(self):
        self.__test_cloudinary_url(options={"secure": True, "cdn_subdomain": True, "secure_cdn_subdomain": False},
                                   expected_url="https://res.cloudinary.com/test123/image/upload/test")

    def test_support_secure_cdn_subdomain_true_override_with_secure(self):
        self.__test_cloudinary_url(
            options={"secure": True, "cdn_subdomain": True, "secure_cdn_subdomain": True, "private_cdn": True},
            expected_url="https://test123-res-2.cloudinary.com/image/upload/test")

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

    def test_escape_public_id_with_non_ascii_characters(self):
        self.__test_cloudinary_url(u"ß", expected_url=DEFAULT_UPLOAD_PATH + "%C3%9F")

    def test_responsive_width(self):
        """should support responsive width"""
        options = {"width": 100, "height": 100, "crop": "crop", "responsive_width": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"responsive": True})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_crop,h_100,w_100/c_limit,w_auto/test")
        cloudinary.config(responsive_width_transformation={"width": "auto", "crop": "pad"})
        options = {"width": 100, "height": 100, "crop": "crop", "responsive_width": True}
        result, options = cloudinary.utils.cloudinary_url("test", **options)
        self.assertEqual(options, {"responsive": True})
        self.assertEqual(result, DEFAULT_UPLOAD_PATH + "c_crop,h_100,w_100/c_pad,w_auto/test")

    def test_norm_range_value(self):
        # should parse integer range values
        self.assertEqual(cloudinary.utils.norm_range_value("200"), "200")
        # should parse float range values
        self.assertEqual(cloudinary.utils.norm_range_value("200.0"), "200.0")
        # should parse a percent range value
        self.assertEqual(cloudinary.utils.norm_range_value("20p"), "20p")
        self.assertEqual(cloudinary.utils.norm_range_value("20P"), "20p")
        self.assertEqual(cloudinary.utils.norm_range_value("20%"), "20p")
        self.assertEqual(cloudinary.utils.norm_range_value("p"), None)

    def test_norm_auto_range_value(self):
        """Should parse both auto and values supported by norm_range_value"""
        self.assertEqual("auto", cloudinary.utils.norm_auto_range_value("auto"))
        self.assertEqual(None, cloudinary.utils.norm_auto_range_value("non_auto"))
        # Should handle regular norm_range_value values
        self.assertEqual(cloudinary.utils.norm_auto_range_value("20P"), "20p")

    def test_fps(self):
        """ Should support a single number, a list of mixed type and a string, including open-ended and closed ranges"""
        fps_test_values = (
            ('24-29.97', 'fps_24-29.97'),
            (24, 'fps_24'),
            (24.973, 'fps_24.973'),
            ('24', 'fps_24'),
            ('-24', 'fps_-24'),
            ('$v', 'fps_$v'),
            ((24, 29.97), 'fps_24-29.97'),
            (['24', '$v'], 'fps_24-$v')
        )
        for value, expected in fps_test_values:
            self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'fps': value},
                                       expected_url=VIDEO_UPLOAD_PATH + expected + "/video_id")

    def test_video_codec(self):
        # should support a string value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_codec': 'auto'},
                                   expected_url=VIDEO_UPLOAD_PATH + "vc_auto/video_id")
        # should support a hash value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video',
                                                                  'video_codec': {'codec': 'h264', 'profile': 'basic',
                                                                                  'level': '3.1'}},
                                   expected_url=VIDEO_UPLOAD_PATH + "vc_h264:basic:3.1/video_id")

        # b_frames=True -> should not add b_frames parameter
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video',
                                                                  'video_codec': {'codec': 'h265', 'profile': 'auto',
                                                                                  'level': 'auto', 'b_frames': True}},
                                   expected_url=VIDEO_UPLOAD_PATH + "vc_h265:auto:auto/video_id")

        # should support a b_frames parameter - b_frames=False -> bframes_no
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video',
                                                                  'video_codec': {'codec': 'h265', 'profile': 'auto',
                                                                                  'level': 'auto', 'b_frames': False}},
                                   expected_url=VIDEO_UPLOAD_PATH + "vc_h265:auto:auto:bframes_no/video_id")

    def test_audio_codec(self):
        # should support a string value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'audio_codec': 'acc'},
                                   expected_url=VIDEO_UPLOAD_PATH + "ac_acc/video_id")

    def test_bit_rate(self):
        # should support an integer value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'bit_rate': 2048},
                                   expected_url=VIDEO_UPLOAD_PATH + "br_2048/video_id")
        # should support "<integer>k"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'bit_rate': '44k'},
                                   expected_url=VIDEO_UPLOAD_PATH + "br_44k/video_id")
        # should support "<integer>m"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'bit_rate': '1m'},
                                   expected_url=VIDEO_UPLOAD_PATH + "br_1m/video_id")

    def test_audio_frequency(self):
        # should support an integer value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'audio_frequency': 44100},
                                   expected_url=VIDEO_UPLOAD_PATH + "af_44100/video_id")

    def test_video_sampling(self):
        # should support an integer value
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_sampling': 20},
                                   expected_url=VIDEO_UPLOAD_PATH + "vs_20/video_id")
        # should support an string value in the a form of \"<float>s\"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'video_sampling': "2.3s"},
                                   expected_url=VIDEO_UPLOAD_PATH + "vs_2.3s/video_id")

    def test_start_offset(self):
        # should support decimal seconds
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': 2.63},
                                   expected_url=VIDEO_UPLOAD_PATH + "so_2.63/video_id")
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': '2.63'},
                                   expected_url=VIDEO_UPLOAD_PATH + "so_2.63/video_id")
        # should support percents of the video length as "<number>p"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': '35p'},
                                   expected_url=VIDEO_UPLOAD_PATH + "so_35p/video_id")
        # should support percents of the video length as "<number>%"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': '35%'},
                                   expected_url=VIDEO_UPLOAD_PATH + "so_35p/video_id")
        # should support auto
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'start_offset': 'auto'},
                                   expected_url=VIDEO_UPLOAD_PATH + "so_auto/video_id")

    def test_end_offset(self):
        # should support decimal seconds
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': 2.63},
                                   expected_url=VIDEO_UPLOAD_PATH + "eo_2.63/video_id")
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': '2.63'},
                                   expected_url=VIDEO_UPLOAD_PATH + "eo_2.63/video_id")
        # should support percents of the video length as "<number>p"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': '35p'},
                                   expected_url=VIDEO_UPLOAD_PATH + "eo_35p/video_id")
        # should support percents of the video length as "<number>%"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'end_offset': '35%'},
                                   expected_url=VIDEO_UPLOAD_PATH + "eo_35p/video_id")

    def test_duration(self):
        # should support decimal seconds
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': 2.63},
                                   expected_url=VIDEO_UPLOAD_PATH + "du_2.63/video_id")
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': '2.63'},
                                   expected_url=VIDEO_UPLOAD_PATH + "du_2.63/video_id")
        # should support percents of the video length as "<number>p"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': '35p'},
                                   expected_url=VIDEO_UPLOAD_PATH + "du_35p/video_id")
        # should support percents of the video length as "<number>%"
        self.__test_cloudinary_url(public_id="video_id", options={'resource_type': 'video', 'duration': '35%'},
                                   expected_url=VIDEO_UPLOAD_PATH + "du_35p/video_id")

    def test_offset(self):
        test_cases = {
            'eo_3.21,so_2.66': '2.66..3.21',
            'eo_3.22,so_2.67': (2.67, 3.22),
            'eo_70p,so_35p': ('35%', '70%'),
            'eo_71p,so_36p': ('36p', '71p'),
            'eo_70.5p,so_35.5p': ['35.5p', '70.5p']
        }
        for transformation, offset in test_cases.items():
            self.__test_cloudinary_url(
                public_id="video_id",
                options={'resource_type': 'video', 'offset': offset},
                expected_url=VIDEO_UPLOAD_PATH + transformation + "/video_id")

    def test_user_agent(self):
        with patch('cloudinary.USER_PLATFORM', ''):
            agent = cloudinary.get_user_agent()
        six.assertRegex(self, agent, r'^CloudinaryPython\/\d\.\d+\.\d+ \(.*; Python \d\.\d+\.\d+\)$')

        platform = 'MyPlatform/1.2.3 (Test code)'
        with patch('cloudinary.USER_PLATFORM', platform):
            result = cloudinary.get_user_agent()
        self.assertEqual(result, platform + ' ' + agent)

    def test_aspect_ratio(self):
        self.__test_cloudinary_url(
            public_id="test",
            options={"aspect_ratio": "1.0"},
            expected_url=DEFAULT_UPLOAD_PATH + "ar_1.0/test")
        self.__test_cloudinary_url(
            public_id="test",
            options={"aspect_ratio": "3:2"},
            expected_url=DEFAULT_UPLOAD_PATH + "ar_3:2/test")
        self.__test_cloudinary_url(
            public_id="test",
            options={"aspect_ratio": Fraction(3.0 / 4)},
            expected_url=DEFAULT_UPLOAD_PATH + "ar_3:4/test")

    def test_overlay_options(self):
        tests = [
            ({'public_id': "logo"}, "logo"),
            ({'public_id': "folder/logo"}, "folder:logo"),
            ({'public_id': "logo", 'type': "private"}, "private:logo"),
            ({'public_id': "logo", 'format': "png"}, "logo.png"),
            ({'resource_type': "video", 'public_id': "cat"}, "video:cat"),
            ({'text': "Hello World, Nice to meet you?", 'font_family': "Arial", 'font_size': "18"},
             "text:Arial_18:Hello%20World%252C%20Nice%20to%20meet%20you%3F"),
            ({'text': "Hello World, Nice to meet you?", 'font_family': "Arial", 'font_size': "18",
              'font_weight': "bold", 'font_style': "italic", 'letter_spacing': 4,
              'line_spacing': 3},
             "text:Arial_18_bold_italic_letter_spacing_4_line_spacing_3:Hello%20World"
             "%252C%20Nice%20to%20meet%20you%3F"),
            ({'resource_type': "subtitles", 'public_id': "sample_sub_en.srt"},
             "subtitles:sample_sub_en.srt"),
            ({'text': "Hello World, Nice to meet you?", 'font_family': "Arial", 'font_size': "18",
              'font_antialiasing': "best", 'font_hinting': "medium"},
             "text:Arial_18_antialias_best_hinting_medium:Hello%20World%252C%20Nice%20to%20meet%20you%3F"),
            ({'resource_type': "subtitles", 'public_id': "sample_sub_he.srt",
              'font_family': "Arial", 'font_size': 40},
             "subtitles:Arial_40:sample_sub_he.srt"),
            ({'url': "https://upload.wikimedia.org/wikipedia/commons/2/2b/고창갯벌.jpg"},
             "fetch:aHR0cHM6Ly91cGxvYWQud2lraW1lZGlhLm9yZy93aWtpcGVkaWEvY29tbW9ucy8yLzJiL-qzoOywveqwr-uyjC5qcGc="),
            ({'url': FETCH_VIDEO_URL, "resource_type": "video"},
             "video:fetch:aHR0cHM6Ly9kZW1vLXJlcy5jbG91ZGluYXJ5LmNvbS92aWRlb3MvZG9nLm1wNA==")
        ]

        for options, expected in tests:
            result = cloudinary.utils.process_layer(options, "overlay")
            self.assertEqual(expected, result)

    def test_text_layer_style_identifier_variables(self):
        options = {
            "transformation": [
                {
                    "variables": [
                        ["$style", "!Arial_12!"],
                    ]
                },
                {
                    "overlay": {
                        "text": "hello-world",
                        "text_style": "$style"
                    }
                }
            ]
        }

        public_id = "sample"
        url, _ = cloudinary.utils.cloudinary_url(public_id, **options)
        self.assertEqual(DEFAULT_UPLOAD_PATH + "$style_!Arial_12!/l_text:$style:hello-world/sample", url)

    def test_overlay_error_1(self):
        """ Must supply font_family for text in overlay """
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url(
                "test", overlay=dict(text="text", font_style="italic"))

    def test_overlay_error_2(self):
        """ Must supply public_id for for non-text underlay """
        with self.assertRaises(ValueError):
            cloudinary.utils.cloudinary_url("test", underlay=dict(resource_type="video"))

    def test_translate_if(self):
        all_operators = "if_"
        all_operators += "w_eq_0_and"
        all_operators += "_h_ne_0_or"
        all_operators += "_ar_lt_0_and"
        all_operators += "_pc_gt_0_and"
        all_operators += "_fc_lte_0_and"
        all_operators += "_w_gte_0"
        all_operators += ",e_grayscale"
        condition = "width = 0 && height != 0 || aspect_ratio < 0 && page_count > 0 " \
                    "and face_count <= 0 and width >= 0"
        options = {"if": condition, "effect": "grayscale"}
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertEqual({}, options)
        self.assertEqual(all_operators, transformation)

    def test_pow_operator(self):
        transformation = {"width": "initial_width ^ 2"}
        normalized = cloudinary.utils.generate_transformation_string(**transformation)[0]
        expected = "w_iw_pow_2"

        self.assertEqual(normalized, expected)

    def test_normalize_expression_with_predefined_variables(self):
        transformation = {"transformation": [{"$width": 10}, {"width": "$width + 10 + width"},]}
        normalized = cloudinary.utils.generate_transformation_string(**transformation)[0]
        expected = "$width_10/w_$width_add_10_add_w"

        self.assertEqual(normalized, expected)

    def test_transformation_with_complex_predefined_variables(self):
        transformation = {
            "transformation": [
                {
                    "variables": [
                        ["$aheight", 300],
                        ["$mywidth", "100"]
                    ]
                },
                {
                    "width": "3 + $mywidth * 3 + 4 / 2 * initialWidth * $mywidth",
                    "height": "3 * initialHeight + $aheight"
                }
            ]
        }

        normalized = cloudinary.utils.generate_transformation_string(**transformation)[0]
        expected = \
            "$aheight_300,$mywidth_100/h_3_mul_ih_add_$aheight,w_3_add_$mywidth_mul_3_add_4_div_2_mul_iw_mul_$mywidth"

        self.assertEqual(normalized, expected)

    def test_merge(self):
        a = {"foo": "foo", "bar": "foo"}
        b = {"foo": "bar"}
        self.assertIsNone(cloudinary.utils.merge(None, None))
        self.assertDictEqual(a, cloudinary.utils.merge(a, None))
        self.assertDictEqual(a, cloudinary.utils.merge(None, a))
        self.assertDictEqual({"foo": "bar", "bar": "foo"}, cloudinary.utils.merge(a, b))
        self.assertDictEqual(a, cloudinary.utils.merge(b, a))

    def test_array_should_define_a_set_of_variables(self):
        options = {
            "if": "face_count > 2",
            "variables": [["$z", 5], ["$foo", "$z * 2"]],
            "crop": "scale",
            "width": "$foo * 200"
        }
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertEqual('if_fc_gt_2,$z_5,$foo_$z_mul_2,c_scale,w_$foo_mul_200', transformation)

    def test_duration_condition(self):
        du_options = {"if": "duration > 30", "crop": "scale", "width": "100"}
        idu_options = {"if": "initial_duration > 30", "crop": "scale", "width": "100"}

        transformation, options = cloudinary.utils.generate_transformation_string(**du_options)
        self.assertEqual("if_du_gt_30,c_scale,w_100", transformation)

        transformation, options = cloudinary.utils.generate_transformation_string(**idu_options)
        self.assertEqual("if_idu_gt_30,c_scale,w_100", transformation)

    def test_dollar_key_should_define_a_variable(self):
        options = {"transformation": [{"$foo": 10}, {"if": "face_count > 2"},
                                      {"crop": "scale", "width": "$foo * 200 / face_count"}, {"if": "end"}]}
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertEqual('$foo_10/if_fc_gt_2/c_scale,w_$foo_mul_200_div_fc/if_end', transformation)

    def test_should_sort_defined_variable(self):
        options = {"$second": 1, "$first": 2}
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertEqual('$first_2,$second_1', transformation)

    def test_should_place_defined_variables_before_ordered(self):
        options = {"variables": [["$z", 5], ["$foo", "$z * 2"]], "$second": 1, "$first": 2}
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertEqual('$first_2,$second_1,$z_5,$foo_$z_mul_2', transformation)

    def test_should_use_context_value_as_user_variables(self):
        options = {"variables": [["$xpos", "ctx:!x_pos!_to_f"], ["$ypos", "ctx:!y_pos!_to_f"]],
                   "crop": "crop", "x": "$xpos * w", "y": "$ypos * h"}
        transformation, options = cloudinary.utils.generate_transformation_string(**options)
        self.assertIn('$xpos_ctx:!x_pos!_to_f,$ypos_ctx:!y_pos!_to_f,c_crop,x_$xpos_mul_w,y_$ypos_mul_h',
                      transformation)

    def test_should_support_text_values(self):
        public_id = "sample"
        options = {"effect": "$efname:100", "$efname": "!blur!"}
        url, options = cloudinary.utils.cloudinary_url(public_id, **options)
        self.assertEqual(DEFAULT_UPLOAD_PATH + "$efname_!blur!,e_$efname:100/sample", url)

    def test_should_support_string_interpolation(self):
        public_id = "sample"
        options = {
            "crop": "scale",
            "overlay": {
                "text": "$(start)Hello $(name)$(ext), $(no ) $( no)$(end)",
                "font_family": "Arial",
                "font_size": "18"
            }
        }
        url, options = cloudinary.utils.cloudinary_url(public_id, **options)
        self.assertEqual(
            DEFAULT_UPLOAD_PATH + "c_scale,l_text:Arial_18:$(start)"
                                  "Hello%20$(name)$(ext)%252C%20%24%28no%20%29"
                                  "%20%24%28%20no%29$(end)/sample",
            url)

    def test_encode_context(self):
        self.assertEqual("", cloudinary.utils.encode_context({}))
        self.assertEqual("a=b", cloudinary.utils.encode_context({"a": "b"}))
        # list values are encoded to a json string
        self.assertEqual('a=["b","c"]', cloudinary.utils.encode_context({"a": ["b", "c"]}))
        # using OrderedDict for tests consistency
        self.assertEqual("a=b|c=d", cloudinary.utils.encode_context(OrderedDict((("a", "b"), ("c", "d")))))
        # test that special characters are unchanged
        self.assertEqual("a=!@#$%^&*()_+<>?,./", cloudinary.utils.encode_context({"a": "!@#$%^&*()_+<>?,./"}))
        # check value escaping
        self.assertEqual(r"a=b\|\|\=|c=d\=a\=\|", cloudinary.utils.encode_context(OrderedDict((("a", "b||="),
                                                                                               ("c", "d=a=|")))))
        # check fallback
        self.assertEqual("not a dict", cloudinary.utils.encode_context("not a dict"))

    def test_build_list_of_dicts(self):
        dict_data = {"one": 1, "two": 2, "three": 3}
        list_of_dict_data = [dict_data]

        # should convert a dict to a list of dict
        self.assertListEqual(list_of_dict_data, build_list_of_dicts(dict_data))

        # should leave as is a list of dict
        self.assertListEqual(list_of_dict_data, build_list_of_dicts(list_of_dict_data))

        # should convert a JSON string representing dict to a list of dict
        string_data = '{"one": 1, "two": 2, "three": 3}'
        self.assertListEqual(list_of_dict_data, build_list_of_dicts(string_data))

        # should convert a JSON string representing a list of dict to a list of dict
        string_array_data = '[{"one": 1, "two": 2, "three": 3}]'
        self.assertListEqual(list_of_dict_data, build_list_of_dicts(string_array_data))

        # should return an empty list on None
        self.assertListEqual([], build_list_of_dicts(None))

        # should return an empty list on []
        self.assertListEqual([], build_list_of_dicts([]))

        # should raise a ValueError on invalid values
        invalid_values = ["", [[]], ["not_a_dict"], [7357], {"not", "a dict"}]
        for invalid_value in invalid_values:
            with self.assertRaises(ValueError):
                build_list_of_dicts(invalid_value)

    def test_json_encode(self):
        # should encode simple values
        self.assertEqual('[]', json_encode(list()))
        self.assertEqual('{}', json_encode(dict()))
        self.assertEqual('[{"k":"v"}]', json_encode([{"k": "v"}, ]))

        # should encode date and datetime to ISO format
        self.assertEqual('{"t":"2019-02-22T16:20:57"}', json_encode({"t": datetime(2019, 2, 22, 16, 20, 57)}))
        self.assertEqual('{"t":"2019-02-22"}', json_encode({"t": date(2019, 2, 22)}))

        # should raise Exception on unsupported values
        with self.assertRaises(TypeError) as te:
            json_encode({"t": self})
        self.assertIn("is not JSON serializable", str(te.exception))

    def test_encode_unicode_url(self):
        self.assertEqual("string", encode_unicode_url("string"))
        self.assertEqual("encoded", encode_unicode_url(u"encoded"))

    def test_base64url_encode(self):
        self.assertEqual("YWQ_Lix4MDl-IUAhYQ==", base64url_encode("ad?.,x09~!@!a"))

    def test_is_remote_url(self):
        self.assertFalse(cloudinary.utils.is_remote_url(TEST_IMAGE))

        remote_urls = [
            "ftp://ftp.cloudinary.com/images/old_logo.png",
            "http://cloudinary.com/images/old_logo.png",
            "https://cloudinary.com/images/old_logo.png",
            "s3://s3-us-west-2.amazonaws.com/cloudinary/images/old_logo.png",
            "gs://cloudinary/images/old_logo.png",
            "data:image/gif;charset=utf8;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
            "data:image/gif;param1=value1;param2=value2;base64," +
            "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
            "data:image/svg+xml;charset=utf-8;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPg",
            CL_BLANK
        ]

        for url in remote_urls:
            self.assertTrue(cloudinary.utils.is_remote_url(url))

    def test_file_io_size(self):
        """Should return correct file size"""
        test_data = b"Test data"
        test_data_len = len(test_data)

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(test_data)

            actual_size = cloudinary.utils.file_io_size(temp_file)

            filesystem_size = getsize(temp_file.name)

            self.assertEqual(test_data_len, filesystem_size)
            self.assertEqual(test_data_len, actual_size)

        with io.BytesIO() as temp_stream:
            temp_stream.write(test_data)

            actual_size = cloudinary.utils.file_io_size(temp_stream)

            self.assertEqual(test_data_len, actual_size)

        with tempfile.NamedTemporaryFile() as empty_file:
            actual_size = cloudinary.utils.file_io_size(empty_file)
            self.assertEqual(0, actual_size)

    def test_cloudinary_scaled_url(self):
        """Should correctly handle format and fetch_format with and without custom transformation"""
        image_format = "jpg"
        fetch_format = "gif"
        resp_w = 99
        resp_trans = "c_scale,w_{}".format(resp_w)
        effect = "sepia"

        options = {"format": image_format, "type": "fetch", "fetch_format": fetch_format}

        # Without custom transformation
        actual_url = cloudinary_scaled_url(FETCH_URL, resp_w, {}, options)

        self.assertEqual("{p}f_{ff}/{t}/{fu}".format(p=DEFAULT_FETCH_PATH, ff=fetch_format, t=resp_trans, fu=FETCH_URL),
                         actual_url)

        # With custom transformation
        actual_url = cloudinary_scaled_url(FETCH_URL, resp_w, self.crop_transformation, options)

        self.assertEqual("{p}c_crop,f_{f},w_100/{t}/{fu}".format(p=DEFAULT_FETCH_PATH, f=image_format, t=resp_trans,
                                                                 fu=FETCH_URL),
                         actual_url)

        # Add base transformation
        options["effect"] = effect
        actual_url = cloudinary_scaled_url(FETCH_URL, resp_w, {}, options)

        self.assertEqual("{p}e_{e},f_{ff}/{t}/{fu}".format(p=DEFAULT_FETCH_PATH, e=effect, ff=fetch_format,
                                                           t=resp_trans, fu=FETCH_URL),
                         actual_url)

        # Should ignore base transformation
        actual_url = cloudinary_scaled_url(FETCH_URL, resp_w, self.crop_transformation, options)

        self.assertEqual("{p}c_crop,f_{f},w_100/{t}/{fu}".format(p=DEFAULT_FETCH_PATH, f=image_format,
                                                                 t=resp_trans, fu=FETCH_URL),
                         actual_url)

        # Should include raw transformation from base options
        options["raw_transformation"] = self.raw_transformation
        actual_url = cloudinary_scaled_url(FETCH_URL, resp_w, {}, options)

        self.assertEqual("{p}e_{e},f_{ff},{rt}/{t}/{fu}".format(p=DEFAULT_FETCH_PATH, e=effect, ff=fetch_format,
                                                                rt=self.raw_transformation, t=resp_trans, fu=FETCH_URL),
                         actual_url)

    def test_build_eager(self):
        test_data = [
            ["should support strings",
             [API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR + "/jpg"],
             "{}|{}/jpg".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should concatenate transformations using pipe",
             [API_TEST_TRANS_SCALE100, API_TEST_TRANS_SEPIA],
             "{}|{}".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should support transformations with multiple components",
             [{"transformation": [API_TEST_TRANS_SCALE100, API_TEST_TRANS_SEPIA]}, API_TEST_TRANS_SEPIA],
             "{}/{}|{}".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should concatenate format at the end of the transformation",
             ([dict(API_TEST_TRANS_SCALE100, **{"format": "gif"}), API_TEST_TRANS_SEPIA]),
             "{}/gif|{}".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should support an empty format",
             ([dict(API_TEST_TRANS_SCALE100, **{"format": ""}), API_TEST_TRANS_SEPIA]),
             "{}/|{}".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should treat a null format as none",
             ([dict(API_TEST_TRANS_SCALE100, **{"format": None}), API_TEST_TRANS_SEPIA]),
             "{}|{}".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should concatenate format at the end of the transformation",
             [dict(API_TEST_TRANS_SCALE100, **{"format": "gif"}),
              dict(API_TEST_TRANS_SEPIA, **{"format": "jpg"})],
             "{}/gif|{}/jpg".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR)],
            ["should support transformations with multiple components and format",
             [{"transformation": [API_TEST_TRANS_SCALE100, API_TEST_TRANS_SEPIA], "format": "gif"},
              API_TEST_TRANS_SEPIA],
             "{}/{}/gif|{}".format(API_TEST_TRANS_SCALE100_STR, API_TEST_TRANS_SEPIA_STR, API_TEST_TRANS_SEPIA_STR)],
        ]

        for message, value, expected in test_data:
            self.assertEqual(expected, build_eager(value), message)

    def test_compute_hash(self):
        self.assertEqual("4de279c82056603e91aab3930a593b8b887d9e48",
                         compute_hex_hash("https://cloudinary.com/images/old_logo.png"))

        original_value = str(uuid.uuid4())

        self.assertEqual(compute_hex_hash(original_value), compute_hex_hash(original_value),
                         "Equal STR inputs should be hashed the same way")

        self.assertNotEqual(compute_hex_hash(original_value), compute_hex_hash("some string"),
                            "Unequal inputs hashes should not match")

    def test_verify_api_response_signature(self):
        public_id = 'tests/logo.png'
        test_version = 1
        api_response_signature = '08d3107a5b2ad82e7d82c0b972218fbf20b5b1e0'

        with patch('cloudinary.config', return_value=cloudinary.config(api_secret=API_SECRET)):
            self.assertTrue(verify_api_response_signature(public_id, test_version, api_response_signature),
                            "The response signature is valid for the same parameters")

            self.assertFalse(verify_api_response_signature(public_id, test_version + 1, api_response_signature),
                             "The response signature is invalid for the wrong version")

        with patch('cloudinary.config', return_value=cloudinary.config(api_secret=None)):
            with self.assertRaises(Exception) as e:
                verify_api_response_signature(public_id, test_version, api_response_signature)
            self.assertEqual(str(e.exception), 'Api secret key is empty')

    def test_verify_api_response_signature_sha256(self):
        public_id = 'tests/logo.png'
        test_version = 1
        api_response_signature = 'cc69ae4ed73303fbf4a55f2ae5fc7e34ad3a5c387724bfcde447a2957cacdfea'

        with patch('cloudinary.config', return_value=cloudinary.config(api_secret=API_SECRET)):
            self.assertTrue(verify_api_response_signature(
                public_id,
                test_version,
                api_response_signature,
                cloudinary.utils.SIGNATURE_SHA256
            ))

    def test_verify_notification_signature(self):
        valid_for = 60
        signature = 'dfe82de1d9083fe0b7ea68070649f9a15b8874da'
        body = '{"notification_type":"eager","eager":[{"transformation":"sp_full_hd/mp4","bytes":1055,' \
               '"url":"http://res.cloudinary.com/demo/video/upload/sp_full_hd/v1533125278/dog.mp4",' \
               '"secure_url":"https://res.cloudinary.com/demo/video/upload/sp_full_hd/v1533125278/dog.mp4"}],' \
               '"public_id":"dog","batch_id":"9b11fa058c61fa577f4ec516bf6ee756ac2aefef095af99aef1302142cc1694a"}'

        with patch('time.time', return_value=MOCKED_NOW):
            valid_response_timestamp = time.time() - valid_for
            test_message_part = "The notification signature is"

            with patch('cloudinary.config', return_value=cloudinary.config(api_secret=API_SECRET)):
                self.assertTrue(verify_notification_signature(body, valid_response_timestamp,
                                                              signature,
                                                              valid_for),
                                "{} valid for matching and not expired signature".format(test_message_part))

                self.assertFalse(verify_notification_signature(body, valid_response_timestamp,
                                                               signature,
                                                               valid_for - 1),
                                 "{} invalid for matching but expired signature".format(test_message_part))

                self.assertFalse(verify_notification_signature(body, valid_response_timestamp,
                                                               signature + 'chars'),
                                 "{} invalid for non matching and not expired signature".format(test_message_part))

                self.assertFalse(verify_notification_signature(body, valid_response_timestamp,
                                                               signature + 'chars',
                                                               valid_for - 1),
                                 "{} invalid for non matching and expired signature".format(test_message_part))
                with self.assertRaises(Exception) as e:
                    verify_notification_signature(1, valid_response_timestamp, signature, valid_for)
                self.assertEqual(str(e.exception), 'Body should be type of string')

            with patch('cloudinary.config', return_value=cloudinary.config(api_secret=None)):
                with self.assertRaises(Exception) as e:
                    verify_notification_signature(body, valid_response_timestamp, signature, valid_for)
                self.assertEqual(str(e.exception), 'Api secret key is empty')

    def test_verify_notification_signature_sha256(self):
        with patch('time.time', return_value=MOCKED_NOW):
            with patch('cloudinary.config', return_value=cloudinary.config(api_secret="someApiSecret")):
                self.assertTrue(verify_notification_signature(
                    "{}",
                    0,
                    "d5497e1a206ad0ba29ad09a7c0c5f22e939682d15009c15ab3199f62fefbd14b",
                    valid_for=time.time(),
                    algorithm=cloudinary.utils.SIGNATURE_SHA256))

    def test_support_long_url_signature(self):
        """should generate short signature by default and long signature if long_url_signature=True"""
        image_name = "sample.jpg"
        short_signature = "s--v2fTPYTu--"
        long_signature = "s--2hbrSMPOjj5BJ4xV7SgFbRDevFaQNUFf--"

        # should create a short signature by default
        self.__test_cloudinary_url(public_id=image_name,
                                   options={"sign_url": True},
                                   expected_url=DEFAULT_UPLOAD_PATH + short_signature + "/" + image_name)

        # should create a long signature when long_url_signature property set to True in the options
        self.__test_cloudinary_url(public_id=image_name,
                                   options={"long_url_signature": True, "sign_url": True},
                                   expected_url=DEFAULT_UPLOAD_PATH + long_signature + "/" + image_name)

        # should create a long signature when long_url_signature property set to True in Cloudinary config
        cloudinary.config().long_url_signature = True
        self.__test_cloudinary_url(public_id=image_name,
                                   options={"sign_url": True},
                                   expected_url=DEFAULT_UPLOAD_PATH + long_signature + "/" + image_name)

    def test_api_sign_request_sha1(self):
        params = dict(cloud_name="dn6ot3ged", timestamp=1568810420, username="user@cloudinary.com")
        signature = api_sign_request(params, "hdcixPpR2iKERPwqvH6sHdK9cyac")
        expected = "14c00ba6d0dfdedbc86b316847d95b9e6cd46d94"
        self.assertEqual(expected, signature)

    def test_api_sign_request_sha256(self):
        params = dict(cloud_name="dn6ot3ged", timestamp=1568810420, username="user@cloudinary.com")
        signature = api_sign_request(params, "hdcixPpR2iKERPwqvH6sHdK9cyac", cloudinary.utils.SIGNATURE_SHA256)
        expected = "45ddaa4fa01f0c2826f32f669d2e4514faf275fe6df053f1a150e7beae58a3bd"
        self.assertEqual(expected, signature)


if __name__ == '__main__':
    unittest.main()
