import os
import time
import unittest

from six import iterkeys
from urllib3 import disable_warnings

import cloudinary
from cloudinary import uploader
from cloudinary.search import Search
from test.helper_test import SUFFIX, TEST_IMAGE, TEST_TAG, UNIQUE_TAG, retry_assertion, cleanup_test_resources_by_tag

TEST_TAG = 'search_{}'.format(TEST_TAG)
UNIQUE_TAG = 'search_{}'.format(UNIQUE_TAG)


TEST_IMAGES_COUNT = 3
MAX_INDEX_RETRIES = 10

public_ids = ["api_test{0}_{1}".format(i, SUFFIX) for i in range(0, TEST_IMAGES_COUNT)]
upload_results = ["++"]

disable_warnings()


class SearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ready = False
        cloudinary.reset_config()
        if not cloudinary.config().api_secret:
            return
        for public_id in public_ids:
            res = uploader.upload(TEST_IMAGE,
                                  public_id=public_id,
                                  tags=[TEST_TAG, UNIQUE_TAG],
                                  context="stage=value")
            upload_results.append(res)
        attempt = 0
        while attempt < MAX_INDEX_RETRIES:
            time.sleep(1)

            results = Search().expression("tags={0}".format(UNIQUE_TAG)).execute()

            if len(results['resources']) == len(public_ids):
                cls.ready = True
                break

            attempt += 1

    def setUp(self):
        if not self.ready:
            self.fail("Failed indexing test resources")

    @classmethod
    def tearDownClass(cls):
        cleanup_test_resources_by_tag([(UNIQUE_TAG,)])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_create_empty_json(self):

        query_hash = Search().as_dict()
        self.assertEqual(query_hash, {})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_add_expression_as_dict(self):

        query = Search().expression('format:jpg').as_dict()
        self.assertEqual(query, {"expression": 'format:jpg'})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_add_sort_by_as_dict(self):

        query = Search().sort_by('created_at', 'asc').sort_by('updated_at', 'desc').as_dict()
        self.assertEqual(query, {"sort_by": [{'created_at': 'asc'}, {'updated_at': 'desc'}]})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_add_max_results_as_dict(self):

        query = Search().max_results('10').as_dict()
        self.assertEqual(query, {"max_results": '10'})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_add_next_cursor_as_dict(self):

        cursor = 'ec471a97ba510904ab57460b3ba3150ec29b6f8563eb1c10f6925ed0c6813f33cfa62ec6cf5ad96be6d6fa3ac3a76ccb'
        query = Search().next_cursor(cursor).as_dict()
        self.assertEqual(query, {"next_cursor": cursor})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_add_aggregations_arguments_as_array_as_dict(self):

        query = Search().aggregate('format').aggregate('size_category').as_dict()
        self.assertEqual(query, {"aggregate": ["format", "size_category"]})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_should_add_with_field_as_dict(self):

        query = Search().with_field('context').with_field('tags').as_dict()
        self.assertEqual(query, {"with_field": ["context", "tags"]})

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skipIf(not os.environ.get('RUN_SEARCH_TESTS', False),
                     "For this test to work, 'Advanced search' should be enabled for your cloud. " +
                     "Use env variable RUN_SEARCH_TESTS=1 if you really want to test it.")
    @retry_assertion()
    def test_should_return_all_images_tagged(self):

        results = Search().expression("tags={0}".format(UNIQUE_TAG)).execute()
        self.assertEqual(len(results['resources']), TEST_IMAGES_COUNT)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skipIf(not os.environ.get('RUN_SEARCH_TESTS', False),
                     "For this test to work, 'Advanced search' should be enabled for your cloud. " +
                     "Use env variable RUN_SEARCH_TESTS=1 if you really want to test it.")
    @retry_assertion()
    def test_should_return_resource(self):

        results = Search().expression("public_id={0}".format(public_ids[0])).execute()
        self.assertEqual(len(results['resources']), 1)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skipIf(not os.environ.get('RUN_SEARCH_TESTS', False),
                     "For this test to work, 'Advanced search' should be enabled for your cloud. " +
                     "Use env variable RUN_SEARCH_TESTS=1 if you really want to test it.")
    @retry_assertion()
    def test_should_paginate_resources_limited_by_tag_and_ordered_by_ascending_public_id(self):
        results = Search().max_results(1).expression("tags={0}".format(UNIQUE_TAG)).sort_by('public_id',
                                                                                            'asc').execute()
        results = {'next_cursor': ''}
        for i in range(0, TEST_IMAGES_COUNT):  # get one resource at a time
            results = Search() \
                .max_results(1) \
                .expression("tags={0}".format(UNIQUE_TAG)) \
                .sort_by('public_id', 'asc') \
                .next_cursor(results['next_cursor']) \
                .execute()
            self.assertEqual(len(results['resources']), 1)
            self.assertEqual(
                results['resources'][0]['public_id'],
                public_ids[i],
                "{0} found public_id {1} instead of {2} ".format(
                    i, results['resources'][0]['public_id'], public_ids[i]))
            self.assertEqual(results['total_count'], TEST_IMAGES_COUNT)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skipIf(not os.environ.get('RUN_SEARCH_TESTS', False),
                     "For this test to work, 'Advanced search' should be enabled for your cloud. " +
                     "Use env variable RUN_SEARCH_TESTS=1 if you really want to test it.")
    @retry_assertion()
    def test_should_include_context(self):

        results = Search().expression("tags={0}".format(UNIQUE_TAG)).with_field('context').execute()
        self.assertEqual(len(results['resources']), TEST_IMAGES_COUNT)
        for res in results['resources']:
            self.assertEqual([key for key in iterkeys(res['context'])], [u'stage'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @unittest.skipIf(not os.environ.get('RUN_SEARCH_TESTS', False),
                     "For this test to work, 'Advanced search' should be enabled for your cloud. " +
                     "Use env variable RUN_SEARCH_TESTS=1 if you really want to test it.")
    @retry_assertion()
    def test_should_include_context_tags_and_image_metadata(self):

        results = Search().expression("tags={0}".format(UNIQUE_TAG)).\
            with_field('context').with_field('tags').\
            with_field('image_metadata').execute()

        self.assertEqual(len(results['resources']), TEST_IMAGES_COUNT)
        for res in results['resources']:
            self.assertEqual([key for key in iterkeys(res['context'])], [u'stage'])
            self.assertTrue('image_metadata' in res)
            self.assertEqual(len(res['tags']), 2)


if __name__ == '__main__':
    unittest.main()
