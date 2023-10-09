from sys import version_info

from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=['ez_setup', 'examples', 'test', 'django_tests', 'django_tests.*']),
    include_package_data=True,
    zip_safe=False,
    test_suite="test",
    tests_require=[
        "mock" + ("<4" if version_info < (3, 6) else "")
    ],
)
