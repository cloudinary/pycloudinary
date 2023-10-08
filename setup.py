from sys import version_info

import setuptools

setuptools.setup(
    test_suite="test",
    tests_require=[
        "mock" + ("<4" if version_info < (3, 6) else "")
    ],
)
