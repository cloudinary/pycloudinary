import os

def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

class Config(object):
  def __init__(self):
    if module_exists('django.conf.settings') and 'CLOUDINARY' in dir(django.conf.settings):
      self.update(django.conf.settings.CLOUDINARY)
    elif os.environ.get("CLOUDINARY_CLOUD_NAME"):
      self.update(
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key = os.environ.get("CLOUDINARY_API_KEY"),
        api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
        secure_distribution = os.environ.get("CLOUDINARY_SECURE_DISTRIBUTION"),
        private_cdn = os.environ.get("CLOUDINARY_PRIVATE_CDN") == 'true'
      )

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

