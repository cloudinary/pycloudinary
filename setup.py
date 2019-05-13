from setuptools import find_packages, setup

version = "1.16.0"

with open('README.rst') as file:
    long_description = file.read()

setup(name='cloudinary',
      version=version,
      description="Python and Django SDK for Cloudinary",
      long_description=long_description,
      keywords='cloudinary image video upload crop resize filter transformation manipulation cdn ',
      author='Cloudinary',
      author_email='info@cloudinary.com',
      url='http://cloudinary.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test', 'django_tests', 'django_tests.*']),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Django",
          "Framework :: Django :: 1.8",
          "Framework :: Django :: 1.9",
          "Framework :: Django :: 1.10",
          "Framework :: Django :: 1.11",
          "Framework :: Django :: 2.0",
          "Framework :: Django :: 2.1",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Multimedia :: Graphics",
          "Topic :: Multimedia :: Graphics :: Graphics Conversion",
          "Topic :: Multimedia :: Sound/Audio",
          "Topic :: Multimedia :: Sound/Audio :: Conversion",
          "Topic :: Multimedia :: Video",
          "Topic :: Multimedia :: Video :: Conversion",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite="test",
      install_requires=[
          "six",
          "mock",
          "urllib3",
          "certifi"
      ],
      )
