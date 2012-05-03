from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pycloudinary',
      version=version,
      description="Python interface to Cloudinary",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='cloudinary image upload cdn',
      author='Tal Lev-Ami',
      author_email='tal.levami@cloudinary.com',
      url='http://cloudinary.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite="tests",                          
      install_requires=["pycurl" ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
