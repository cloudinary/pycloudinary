import contextlib
import unittest

from cloudinary.utils import normalize_expression, generate_transformation_string, _SIMPLE_TRANSFORMATION_PARAMS

NORMALIZATION_EXAMPLES = {
    'None is not affected': [None, None],
    'number replaced with a string value': [10, '10'],
    'empty string is not affected': ['', ''],
    'single space is replaced with a single underscore': [' ', '_'],
    'blank string is replaced with a single underscore': ['   ', '_'],
    'underscore is not affected': ['_', '_'],
    'sequence of underscores and spaces is replaced with a single underscore': [' _ __  _', '_'],
    'arbitrary text is not affected': ['foobar', 'foobar'],
    'double ampersand replaced with and operator': ['foo && bar', 'foo_and_bar'],
    'double ampersand with no space at the end is not affected': ['foo&&bar', 'foo&&bar'],
    'width recognized as variable and replaced with w': ['width', 'w'],
    'initial aspect ratio recognized as variable and replaced with iar': ['initial_aspect_ratio', 'iar'],
    'duration is recognized as a variable and replaced with du': ['duration', 'du'],
    'duration after : is not a variable and is not affected': ['preview:duration_2', 'preview:duration_2'],
    '$width recognized as user variable and not affected': ['$width', '$width'],
    '$initial_aspect_ratio recognized as user variable followed by aspect_ratio variable': [
        '$initial_aspect_ratio',
        '$initial_ar',
    ],
    '$mywidth recognized as user variable and not affected': ['$mywidth', '$mywidth'],
    '$widthwidth recognized as user variable and not affected': ['$widthwidth', '$widthwidth'],
    '$_width recognized as user variable and not affected': ['$_width', '$_width'],
    '$__width recognized as user variable and not affected': ['$__width', '$_width'],
    '$$width recognized as user variable and not affected': ['$$width', '$$width'],
    '$height recognized as user variable and not affected': ['$height_100', '$height_100'],
    '$heightt_100 recognized as user variable and not affected': ['$heightt_100', '$heightt_100'],
    '$$height_100 recognized as user variable and not affected': ['$$height_100', '$$height_100'],
    '$heightmy_100 recognized as user variable and not affected': ['$heightmy_100', '$heightmy_100'],
    '$myheight_100 recognized as user variable and not affected': ['$myheight_100', '$myheight_100'],
    '$heightheight_100 recognized as user variable and not affected': [
        '$heightheight_100',
        '$heightheight_100',
    ],
    '$theheight_100 recognized as user variable and not affected': ['$theheight_100', '$theheight_100'],
    '$__height_100 recognized as user variable and not affected': ['$__height_100', '$_height_100']
}


class ExpressionNormalizationTest(unittest.TestCase):

    def test_expression_normalization(self):
        for description, (input_expression, expected_expression) in NORMALIZATION_EXAMPLES.items():
            with self.subTest(description, input_expression=input_expression):
                self.assertEqual(expected_expression, normalize_expression(input_expression))

    def test_predefined_parameters_normalization(self):
        normalized_params = (
            'angle',
            'aspect_ratio',
            'dpr',
            'effect',
            'height',
            'opacity',
            'quality',
            'width',
            'x',
            'y',
            'start_offset',
            'end_offset',
            'zoom'
        )

        value = 'width * 2'
        normalized_value = 'w_mul_2'

        for param in normalized_params:
            with self.subTest('should normalize value in {}'.format(param), param=param):

                options = {param: value}

                # Set no_html_sizes
                if param in ['height', 'width']:
                    options['crop'] = 'fit'

                result = generate_transformation_string(**options)

                self.assertEqual(result[1], {})
                self.assertFalse(value in result[0])
                self.assertTrue(normalized_value in result[0])

    def test_simple_parameters_normalization(self):
        value = 'width * 2'
        normalized_value = 'w_mul_2'
        not_normalized_params = list(_SIMPLE_TRANSFORMATION_PARAMS.values())
        not_normalized_params.extend(['overlay', 'underlay'])

        for param in not_normalized_params:
            with self.subTest('should not normalize value in {}'.format(param), param=param):
                options = {param: value}

                result = generate_transformation_string(**options)

                self.assertTrue(value in result[0])
                self.assertFalse(normalized_value in result[0])

    def test_support_start_offset(self):
        result = generate_transformation_string(**{"width": "100", "start_offset": "idu - 5"})
        self.assertIn("so_idu_sub_5", result[0])

        result = generate_transformation_string(**{"width": "100", "start_offset": "$logotime"})
        self.assertIn("so_$logotime", result[0])

    def test_support_end_offset(self):
        result = generate_transformation_string(**{"width": "100", "end_offset": "idu - 5"})
        self.assertIn("eo_idu_sub_5", result[0])

        result = generate_transformation_string(**{"width": "100", "end_offset": "$logotime"})
        self.assertIn("eo_$logotime", result[0])

    if not hasattr(unittest.TestCase, "subTest"):
        # Support Python before version 3.4
        @contextlib.contextmanager
        def subTest(self, msg="", **params):
            yield
