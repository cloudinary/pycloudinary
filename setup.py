from setuptools import setup, find_packages

version = '1.4.0'

setup(name='cloudinary',
      version=version,
      description="Python interface to Cloudinary",
      long_description='',
      keywords='cloudinary image upload transformation cdn',
      author='Cloudinary',
      author_email='info@cloudinary.com',
      url='http://cloudinary.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'django_tests', 'django_tests.*']),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite="tests",
      install_requires=[
          "six",
          "urllib3"
      ],
      )
