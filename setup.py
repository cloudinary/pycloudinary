from setuptools import setup, find_packages
import sys, os

version = '0.2.0'

setup(name='pycloudinary',
      version=version,
      description="Python interface to Cloudinary",
      long_description='',
      classifiers=[], 
      keywords='cloudinary image upload transformation cdn',
      author='Cloudinary',
      author_email='info@cloudinary.com',
      url='http://cloudinary.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite="tests",                          
      install_requires=["poster"]
      )
