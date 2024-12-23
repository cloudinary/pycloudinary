[![Build Status](https://app.travis-ci.com/cloudinary/pycloudinary.svg)](https://app.travis-ci.com/cloudinary/pycloudinary)
[![PyPI Version](https://img.shields.io/pypi/v/cloudinary.svg)](https://pypi.python.org/pypi/cloudinary/)
[![PyPI PyVersions](https://img.shields.io/pypi/pyversions/cloudinary.svg)](https://pypi.python.org/pypi/cloudinary/)
[![PyPI DjangoVersions](https://img.shields.io/pypi/djversions/cloudinary.svg)](https://pypi.python.org/pypi/cloudinary/)
[![PyPI Version](https://img.shields.io/pypi/dm/cloudinary.svg)](https://pypi.python.org/pypi/cloudinary/)
[![PyPI License](https://img.shields.io/pypi/l/cloudinary.svg)](https://pypi.python.org/pypi/cloudinary/)


Cloudinary Python SDK
==================

## About
The Cloudinary Python SDK allows you to quickly and easily integrate your application with Cloudinary.
Effortlessly optimize, transform, upload and manage your cloud's assets.


#### Note
This Readme provides basic installation and usage information.
For the complete documentation, see the [Python SDK Guide](https://cloudinary.com/documentation/django_integration).

## Table of Contents
- [Key Features](#key-features)
- [Version Support](#Version-Support)
- [Installation](#installation)
- [Usage](#usage)
    - [Setup](#Setup)
    - [Transform and Optimize Assets](#Transform-and-Optimize-Assets)
    - [Django](#Django)


## Key Features
- [Transform](https://cloudinary.com/documentation/django_video_manipulation#video_transformation_examples) and
  [optimize](https://cloudinary.com/documentation/django_image_manipulation#image_optimizations) assets.
- Generate [image](https://cloudinary.com/documentation/django_image_manipulation#deliver_and_transform_images) and
  [video](https://cloudinary.com/documentation/django_video_manipulation#django_video_transformation_code_examples) tags.
- [Asset Management](https://cloudinary.com/documentation/django_asset_administration).
- [Secure URLs](https://cloudinary.com/documentation/video_manipulation_and_delivery#generating_secure_https_urls_using_sdks).



## Version Support

| SDK Version | Python 2.7 | Python 3.x |
|-------------|------------|------------|
| 1.x         | ✔          | ✔          |

| SDK Version | Django 1.11 | Django 2.x | Django 3.x | Django 4.x | Django 5.x |
|-------------|-------------|------------|------------|------------|------------|
| 1.x         | ✔           | ✔          | ✔          | ✔          | ✔          |


## Installation
```bash
pip install cloudinary
```

# Usage

### Setup
```python
import cloudinary
```

### Transform and Optimize Assets
- [See full documentation](https://cloudinary.com/documentation/django_image_manipulation).

```python 
cloudinary.utils.cloudinary_url("sample.jpg", width=100, height=150, crop="fill")
```

### Upload
- [See full documentation](https://cloudinary.com/documentation/django_image_and_video_upload).
- [Learn more about configuring your uploads with upload presets](https://cloudinary.com/documentation/upload_presets).
```python
cloudinary.uploader.upload("my_picture.jpg")
```

### Django
- [See full documentation](https://cloudinary.com/documentation/django_image_and_video_upload#django_forms_and_models).

### Security options
- [See full documentation](https://cloudinary.com/documentation/solution_overview#security).

### Sample projects
- [Sample projects](https://github.com/cloudinary/pycloudinary/tree/master/samples).
- [Django Photo Album](https://github.com/cloudinary/cloudinary-django-sample).


## Contributions
- Ensure tests run locally.
- Open a PR and ensure Travis tests pass.
- See [CONTRIBUTING](CONTRIBUTING.md).

## Get Help
If you run into an issue or have a question, you can either:
- Issues related to the SDK: [Open a GitHub issue](https://github.com/cloudinary/pycloudinary/issues).
- Issues related to your account: [Open a support ticket](https://cloudinary.com/contact).


## About Cloudinary
Cloudinary is a powerful media API for websites and mobile apps alike, Cloudinary enables developers to efficiently 
manage, transform, optimize, and deliver images and videos through multiple CDNs. Ultimately, viewers enjoy responsive 
and personalized visual-media experiences—irrespective of the viewing device.


## Additional Resources
- [Cloudinary Transformation and REST API References](https://cloudinary.com/documentation/cloudinary_references): Comprehensive references, including syntax and examples for all SDKs.
- [MediaJams.dev](https://mediajams.dev/): Bite-size use-case tutorials written by and for Cloudinary Developers
- [DevJams](https://www.youtube.com/playlist?list=PL8dVGjLA2oMr09amgERARsZyrOz_sPvqw): Cloudinary developer podcasts on YouTube.
- [Cloudinary Academy](https://training.cloudinary.com/): Free self-paced courses, instructor-led virtual courses, and on-site courses.
- [Code Explorers and Feature Demos](https://cloudinary.com/documentation/code_explorers_demos_index): A one-stop shop for all code explorers, Postman collections, and feature demos found in the docs.
- [Cloudinary Roadmap](https://cloudinary.com/roadmap): Your chance to follow, vote, or suggest what Cloudinary should develop next.
- [Cloudinary Facebook Community](https://www.facebook.com/groups/CloudinaryCommunity): Learn from and offer help to other Cloudinary developers.
- [Cloudinary Account Registration](https://cloudinary.com/users/register/free): Free Cloudinary account registration.
- [Cloudinary Website](https://cloudinary.com): Learn about Cloudinary's products, partners, customers, pricing, and more.


## Licence
Released under the MIT license.
