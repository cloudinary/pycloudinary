from sys import version_info

from setuptools import find_packages, setup

if version_info[0] >= 3:
    setup()
else:
    # Following code is legacy (Python 2.7 compatibility) and will be removed in the future!
    # TODO: Remove in next major update (when dropping Python 2.7 compatibility)
    version = "1.43.0"

    with open('README.md') as file:
        long_description = file.read()

    setup(name='cloudinary',
          version=version,
          description="Python and Django SDK for Cloudinary",
          long_description=long_description,
          long_description_content_type='text/markdown',
          keywords='cloudinary image video upload crop resize filter transformation manipulation cdn ',
          author='Cloudinary',
          author_email='info@cloudinary.com',
          url='https://cloudinary.com',
          project_urls={
              'Source': 'https://github.com/cloudinary/pycloudinary',
              'Changelog ': 'https://raw.githubusercontent.com/cloudinary/pycloudinary/master/CHANGELOG.md'
          },
          license='MIT',
          packages=find_packages(exclude=['ez_setup', 'examples', 'test', 'django_tests', 'django_tests.*']),
          classifiers=[
              "Development Status :: 5 - Production/Stable",
              "Environment :: Web Environment",
              "Framework :: Django",
              "Framework :: Django :: 1.11",
              "Framework :: Django :: 2.2",
              "Framework :: Django :: 3.2",
              "Framework :: Django :: 4.2",
              "Framework :: Django :: 5.0",
              "Framework :: Django :: 5.1",
              "Intended Audience :: Developers",
              "License :: OSI Approved :: MIT License",
              "Programming Language :: Python",
              "Programming Language :: Python :: 2",
              "Programming Language :: Python :: 2.7",
              "Programming Language :: Python :: 3",
              "Programming Language :: Python :: 3.9",
              "Programming Language :: Python :: 3.10",
              "Programming Language :: Python :: 3.11",
              "Programming Language :: Python :: 3.12",
              "Programming Language :: Python :: 3.13",
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
              "urllib3>=1.26.5",
              "certifi"
          ],
          tests_require=[
              "mock<4",
              "pytest"
          ],
          )
