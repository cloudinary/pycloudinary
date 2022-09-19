import six
from django.test import TestCase

import cloudinary
from platform import platform as pf


class TestUserAgent(TestCase):
    def test_django_user_agent(self):
        agent = cloudinary.get_user_agent()

        os_info = pf().lower()
        os_info = os_info.split("-")

        six.assertRegex(self, agent, r'^Django\/\d\.\d+\.?\d* CloudinaryPython\/\d\.\d+\.\d+ \(Python \d\.\d+\.\d+\/{}\)$'.format(os_info[0].capitalize()))
