from setuptools import setup, find_packages

version = '1.0.21'

setup(name='cloudinary',
      version=version,
      description="Python interface to Cloudinary",
      long_description='',
      keywords='cloudinary image upload transformation cdn',
      author='Cloudinary',
      author_email='info@cloudinary.com',
      url='http://cloudinary.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite="tests"
      )
