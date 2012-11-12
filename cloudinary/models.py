from cloudinary import forms, utils
from cloudinary.storage import CloudinaryStorage
from django.db import models
from django.db.models.fields.files import ImageFieldFile

# Ensure South doesn't explode on this field
try:
    import south.modelsinspector
except ImportError:
    pass
else:
    south.modelsinspector.add_introspection_rules(
        [],
        ["^cloudinary\.models\.CloudinaryField"]
    )


class CloudinaryFieldFile(ImageFieldFile):

  def save(self, name, content, save=True):
    if isinstance(content, str):
        content = StringWithSize(content)
    super(CloudinaryFieldFile, self).save(name, content, save)

  def url_with_options(self, **options):
    return utils.cloudinary_url(self.name, **options)[0]


class StringWithSize(str):
  size = 0


class CloudinaryField(models.ImageField):

  attr_class = CloudinaryFieldFile
  description = "An image stored in Cloudinary"

  def __init__(self, *args, **kwargs):
    for arg in ('storage', 'upload_to'):
        if arg in kwargs:
            raise TypeError("'%s' cannot be modified for %s." % (arg, self.__class__))

    options = {
      'storage': CloudinaryStorage(),
      'upload_to': '/',
    }
    options.update(kwargs)
    super(CloudinaryField, self).__init__(*args, **options)

  def formfield(self, **kwargs):
      defaults = {'form_class': forms.CloudinaryFileField}
      defaults.update(kwargs)
      return super(CloudinaryField, self).formfield(**defaults)
