import six
from django.test import TestCase

import cloudinary


class TestUserAgent(TestCase):
    def test_django_user_agent(self):
        agent = cloudinary.get_user_agent()

        six.assertRegex(self, agent, r'^Django\/\d\.\d+\.?\d* CloudinaryPython\/\d\.\d+\.\d+ \(Python \d\.\d+\.\d+\)$')
