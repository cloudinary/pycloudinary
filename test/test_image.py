import copy
import logging
import os
import re
import unittest

import six
from mock import mock

import cloudinary
from cloudinary import CloudinaryImage


class ImageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger = cloudinary.logger

        if os.getenv("DEBUG"):
            cls.logger.setLevel(logging.DEBUG)

    def setUp(self):
        self.cloud_name = 'test123'
        self.public_id = "sample"
        self.image_format = "jpg"
        self.full_public_id = "{id}.{format}".format(id=self.public_id, format=self.image_format)
        self.upload_url = "http://res.cloudinary.com/{cloud_name}/image/upload".format(cloud_name=self.cloud_name)
        self.common_format = {"url": self.upload_url, "id": self.full_public_id}
        self.image = CloudinaryImage(self.public_id, format=self.image_format)

        self.common_image_options = {"effect": "sepia", "cloud_name": self.cloud_name}
        self.common_transformation_str = 'e_sepia'
        self.breakpoint_list = [100, 200, 300, 399]
        self.common_srcset = {"breakpoints": self.breakpoint_list}
        self.custom_attributes = {'custom_attr1': 'custom_value1', 'custom_attr2': 'custom_value2'}

        cloudinary.reset_config()
        cloudinary.config(cloud_name=self.cloud_name, api_secret="1234", cname=None)

    def test_build_url(self):
        """should generate url """
        self.assertEqual(self.image.build_url(), '{url}/{id}'.format(**self.common_format))

    def test_url(self):
        """should url property """
        self.assertEqual(self.image.url, '{url}/{id}'.format(**self.common_format))

    def test_image(self):
        """should generate image """
        self.assertEqual(self.image.image(), '<img src="{url}/{id}"/>'.format(**self.common_format))

    def test_image_unicode(self):
        """should generate image with unicode arguments """
        self.assertEqual(
            self.image.image(alt=u"\ua000abcd\u07b4"),
            u'<img alt="\ua000abcd\u07b4" src="{url}/{id}"/>'.format(**self.common_format))

    def test_scale(self):
        """should accept scale crop and pass width/height to image tag """
        self.assertEqual(
            self.image.image(crop="scale", width=100, height=100),
            '<img height="100" src="{url}/c_scale,h_100,w_100/{id}" width="100"/>'.format(**self.common_format))

    def test_validate(self):
        """should validate signature """
        self.assertFalse(self.image.validate())
        self.assertFalse(CloudinaryImage("hello", format="png", version="1234", signature="1234").validate())
        self.assertTrue(CloudinaryImage("hello", format="png", version="1234",
                                        signature="2aa73bf69fb50816e5509e32275b8c417dcb880d").validate())

    def test_responsive_width(self):
        """should add responsive width transformation"""
        self.assertEqual(self.image.image(responsive_width=True),
                         '<img class="cld-responsive" data-src="{url}/c_limit,w_auto/{id}"/>'.format(
                             **self.common_format))

    def test_width_auto(self):
        """should support width=auto """
        self.assertEqual(self.image.image(width="auto", crop="limit"),
                         '<img class="cld-responsive" data-src="{url}/c_limit,w_auto/{id}"/>'.format(
                             **self.common_format))

    def test_dpr_auto(self):
        """should support dpr=auto """
        self.assertEqual(self.image.image(dpr="auto"),
                         '<img class="cld-hidpi" data-src="{url}/dpr_auto/{id}"/>'.format(**self.common_format))

    def test_effect_art_incognito(self):
        """should support effect art:incognito """
        e = "art:incognito"
        self.assertEqual(self.image.image(effect=e), '<img src="{url}/e_{e}/{id}"/>'.format(e=e, **self.common_format))

    def shared_client_hints(self, **options):
        """should not use data-src or set responsive class"""
        tag = CloudinaryImage(self.full_public_id).image(**options)
        six.assertRegex(self, tag, '<img.*>', "should not use data-src or set responsive class")
        self.assertIsNone(re.match('<.* class.*>', tag), "should not use data-src or set responsive class")
        self.assertIsNone(re.match('\bdata-src\b', tag), "should not use data-src or set responsive class")
        expected_re = 'src=["\']{url}/c_scale,dpr_auto,w_auto/{id}["\']'.format(**self.common_format)
        six.assertRegex(self, tag, expected_re, "should not use data-src or set responsive class")
        cloudinary.config(responsive=True)
        tag = CloudinaryImage(self.full_public_id).image(**options)
        six.assertRegex(self, tag, '<img.*>')
        self.assertIsNone(re.match('<.* class.*>', tag), "should override responsive")
        self.assertIsNone(re.match('\bdata-src\b', tag), "should override responsive")

        six.assertRegex(self, tag, expected_re, "should override responsive")

    def test_client_hints_as_options(self):
        self.shared_client_hints(dpr="auto", cloud_name=self.cloud_name, width="auto", crop="scale", client_hints=True)

    def test_client_hints_as_global(self):
        cloudinary.config(client_hints=True)
        self.shared_client_hints(dpr="auto", cloud_name=self.cloud_name, width="auto", crop="scale")

    def test_client_hints_as_false(self):
        """should use normal responsive behaviour"""
        cloudinary.config(responsive=True)
        tag = CloudinaryImage(self.full_public_id).image(width="auto", crop="scale", cloud_name=self.cloud_name,
                                                         client_hints=False)
        six.assertRegex(self, tag, '<img.*>')
        six.assertRegex(self, tag, 'class=["\']cld-responsive["\']')
        exp = 'data-src=["\']{url}/c_scale,w_auto/{id}["\']'.format(**self.common_format)
        six.assertRegex(self, tag, exp)

    def test_width_auto_breakpoints(self):
        """supports auto width"""
        tag = CloudinaryImage(self.full_public_id).image(crop="scale", dpr="auto", cloud_name=self.cloud_name,
                                                         width="auto:breakpoints", client_hints=True)
        expected_re = 'src=["\']{url}/c_scale,dpr_auto,w_auto:breakpoints/{id}["\']'.format(**self.common_format)
        six.assertRegex(self, tag, expected_re)

    def _get_expected_cl_image_tag(self, public_id, common_trans_str, custom_trans_str=None, srcset_breakpoints=None,
                                   attributes=None):
        """
        Helper method for generating expected image tag

        :param public_id:           Public ID of the image
        :param common_trans_str:    Default transformation string to be used in all resources
        :param custom_trans_str:    Optional custom transformation string to be be used inside srcset resources.
                                    If not provided, common_trans_str is used
        :param srcset_breakpoints:  Optional list of breakpoints for srcset. If not provided srcset is omitted
        :param attributes:          Optional dict of custom attributes to be added to the tag

        :return: Resulting image tag
        """
        if not custom_trans_str:
            custom_trans_str = common_trans_str

        if attributes is None:
            attributes = dict()

        if srcset_breakpoints:
            bp_template = "{upload_url}/{custom_trans_str}/c_scale,w_{{w}}/{public_id} {{w}}w".format(
                upload_url=self.upload_url, custom_trans_str=custom_trans_str, public_id=public_id)
            attributes['srcset'] = ', '.join(bp_template.format(w=bp) for bp in srcset_breakpoints)

        attributes["src"] = "{upload_url}/{common_trans_str}/{public_id}".format(
            upload_url=self.upload_url, common_trans_str=common_trans_str, public_id=public_id)

        attributes_str = " ".join(
            '{k}="{v}"'.format(k=k, v=attributes[k]) for k in sorted(attributes)) if attributes else ""

        tag = "<img"

        if attributes_str:
            tag += " " + attributes_str

        tag += "/>"
        return tag

    def test_srcset_from_breakpoints(self):
        """Should create srcset attribute with provided breakpoints"""
        tag = CloudinaryImage(self.full_public_id).image(srcset=self.common_srcset, **self.common_image_options)
        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       srcset_breakpoints=self.breakpoint_list)
        self.assertEqual(expected_tag, tag)

    def test_srcset_from_float_breakpoints(self):
        """Should create srcset attribute with provided breakpoints as float values"""
        float_breakpoint_list = [bp + 0.1 for bp in self.breakpoint_list]
        self.common_srcset = {"breakpoints": float_breakpoint_list}
        tag = CloudinaryImage(self.full_public_id).image(srcset=self.common_srcset, **self.common_image_options)
        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       srcset_breakpoints=float_breakpoint_list)
        self.assertEqual(expected_tag, tag)

    def test_srcset_from_min_width_max_width_max_images(self):
        """Should support srcset attribute defined by min_width, max_width, and max_images"""
        srcset_params = {"min_width": self.breakpoint_list[0], "max_width": self.breakpoint_list[-1],
                         "max_images": len(self.breakpoint_list)}

        tag = CloudinaryImage(self.full_public_id).image(srcset=srcset_params, **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       srcset_breakpoints=self.breakpoint_list)
        self.assertEqual(expected_tag, tag)

    def test_srcset_with_one_image(self):
        """Should support 1 image in srcset"""
        srcset_params = {"min_width": self.breakpoint_list[0], "max_width": self.breakpoint_list[-1],
                         "max_images": 1}

        tag_by_params = CloudinaryImage(self.full_public_id).image(srcset=srcset_params, **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       srcset_breakpoints=[self.breakpoint_list[-1]])
        self.assertEqual(expected_tag, tag_by_params)

        srcset_breakpoint = {"breakpoints": [self.breakpoint_list[-1]]}
        tag_by_breakpoint = CloudinaryImage(self.full_public_id).image(srcset=srcset_breakpoint,
                                                                       **self.common_image_options)
        self.assertEqual(expected_tag, tag_by_breakpoint)

    def test_srcset_with_custom_transformation(self):
        """Should support custom transformation for srcset items"""
        srcset_params = copy.deepcopy(self.common_srcset)
        srcset_params["transformation"] = {"crop": "crop", "width": 10, "height": 20}
        custom_transformation_str = "c_crop,h_20,w_10"

        tag = CloudinaryImage(self.full_public_id).image(srcset=srcset_params, **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       custom_trans_str=custom_transformation_str,
                                                       srcset_breakpoints=self.breakpoint_list)
        self.assertEqual(expected_tag, tag)

    def test_srcset_with_sizes_attribute(self):
        """Should populate sizes attribute"""
        srcset_params = copy.deepcopy(self.common_srcset)
        srcset_params["sizes"] = True
        tag = CloudinaryImage(self.full_public_id).image(srcset=srcset_params, **self.common_image_options)

        expected_sizes_attr = ", ".join("(max-width: {w}px) {w}px".format(w=bp) for bp in self.breakpoint_list)
        attributes = {"sizes": expected_sizes_attr}
        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       srcset_breakpoints=self.breakpoint_list, attributes=attributes)
        self.assertEqual(expected_tag, tag)

    def test_srcset_from_string(self):
        """Should support srcset string value"""
        raw_srcset_value = "some srcset data as is"
        attributes = {"srcset": raw_srcset_value}

        tag = CloudinaryImage(self.full_public_id).image(attributes=attributes, **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       attributes=attributes)
        self.assertEqual(expected_tag, tag)

        legacy_tag = CloudinaryImage(self.full_public_id).image(srcset=raw_srcset_value, **self.common_image_options)
        self.assertEqual(expected_tag, legacy_tag)

    def test_srcset_width_height_removed(self):
        """Should remove width and height attributes in case srcset is specified, but passed to transformation"""
        tag = CloudinaryImage(self.full_public_id).image(width=500, height=500, srcset=self.common_srcset,
                                                         **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id,
                                                       self.common_transformation_str + ",h_500,w_500",
                                                       srcset_breakpoints=self.breakpoint_list)
        self.assertEqual(expected_tag, tag)

    def test_srcset_invalid_values(self):
        """Should raise ValueError on invalid values"""
        invalid_srcset_params = [
            {'sizes': True},                                          # srcset data not provided
            {'max_width': 300, 'max_images': 3},                      # no min_width
            {'min_width': '1', 'max_width': 300, 'max_images': 3},    # invalid min_width
            {'min_width': 100, 'max_images': 3},                      # no max_width
            {'min_width': 100, 'max_width': '3', 'max_images': 3},    # invalid max_width
            {'min_width': 200, 'max_width': 100, 'max_images': 3},    # min_width > max_width
            {'min_width': 100, 'max_width': 300},                     # no max_images
            {'min_width': 100, 'max_width': 300, 'max_images': 0},    # invalid max_images
            {'min_width': 100, 'max_width': 300, 'max_images': -17},  # invalid max_images
            {'min_width': 100, 'max_width': 300, 'max_images': '3'},  # invalid max_images
        ]
        with mock.patch('cloudinary.logger') as log_mock:
            for invalid_srcset in invalid_srcset_params:
                image_tag = CloudinaryImage(self.full_public_id).image(srcset=invalid_srcset,
                                                                       **self.common_image_options)
                self.assertNotIn("srcset", image_tag)

            expected_log_call_count = len(invalid_srcset_params) + 1  # When `sizes` is True we call log twice
            self.assertEqual(expected_log_call_count, log_mock.warning.call_count)

    def test_custom_attributes(self):
        """ Should consume custom attributes from 'attributes' key"""
        tag = CloudinaryImage(self.full_public_id).image(attributes=self.custom_attributes, **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       attributes=self.custom_attributes)
        self.assertEqual(expected_tag, tag)

    def test_custom_attributes_legacy(self):
        """ Should consume custom attributes as is from options"""
        custom_options = copy.deepcopy(self.common_image_options)
        custom_options.update(self.custom_attributes)
        tag = CloudinaryImage(self.full_public_id).image(**custom_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       attributes=self.custom_attributes)
        self.assertEqual(expected_tag, tag)

    def test_custom_attributes_override_existing(self):
        """ Attributes from 'attributes' dict should override existing attributes"""
        updated_attributes = {"alt": "updated alt"}
        tag = CloudinaryImage(self.full_public_id).image(alt="original alt", attributes=updated_attributes,
                                                         **self.common_image_options)

        expected_tag = self._get_expected_cl_image_tag(self.full_public_id, self.common_transformation_str,
                                                       attributes=updated_attributes)
        self.assertEqual(expected_tag, tag)


if __name__ == "__main__":
    unittest.main()
