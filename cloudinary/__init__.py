from __future__ import absolute_import
 
import os
from cloudinary import utils
from urlparse import urlparse

def import_django_settings():
  try:
    import django.conf
    if 'CLOUDINARY' in dir(django.conf.settings):
      return django.conf.settings.CLOUDINARY
    else:
      return None
  except ImportError:
    return None

class Config(object):
  def __init__(self):
    django_settings = import_django_settings()
    if django_settings:
      self.update(**django_settings)
    elif os.environ.get("CLOUDINARY_CLOUD_NAME"):
      self.update(
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key = os.environ.get("CLOUDINARY_API_KEY"),
        api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
        secure_distribution = os.environ.get("CLOUDINARY_SECURE_DISTRIBUTION"),
        private_cdn = os.environ.get("CLOUDINARY_PRIVATE_CDN") == 'true'
      )
    elif os.environ.get("CLOUDINARY_URL"):
      uri = urlparse(os.environ.get("CLOUDINARY_URL"))
      self.update(
        cloud_name = uri.hostname,
        api_key = uri.username,
        api_secret = uri.password,
        private_cdn = uri.path != ''
      )
      if uri.path != '': 
        self.update(secure_distribution = uri.path[1:]) 
  def __getattr__(self, i):
    if i in self.__dict__:
      return self.__dict__[i]
    else:
      return None

  def update(self, **keywords):
    for k, v in keywords.items():
      self.__dict__[k] = v

_config = Config()

def config(**keywords):
  global _config
  _config.update(**keywords)
  return _config

def reset_config():
  global _config
  _config = Config()

class CloudinaryImage(object):
  def __init__(self, public_id, format = None, version = None, signature = None):
    self.public_id = public_id
    self.format = format
    self.version = version
    self.signature = signature

  def validate(self):
    expected = utils.api_sign_request({"public_id": self.public_id, "version": self.version}, config().api_secret)
    return self.signature == expected
   
  def url(self, **options):
    options.update(format = self.format, version = self.version)
    return utils.cloudinary_url(self.public_id, **options)[0]

  def image(self, **options):
    options.update(format = self.format, version = self.version)
    src, attrs = utils.cloudinary_url(self.public_id, **options)
    return u"<img src='{0}' {1}/>".format(src, ' '.join(sorted([u"{0}='{1}'".format(key, value) for key, value in attrs.items() if value])))


