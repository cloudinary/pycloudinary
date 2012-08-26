import re
from cloudinary import CloudinaryImage, forms
from django.db import models

class CloudinaryField(models.Field):

  description = "An image stored in Cloudinary"

  __metaclass__ = models.SubfieldBase

  def __init__(self, *args, **kwargs):
    options = {'max_length': 100}
    self.default_form_class = kwargs.pop("default_form_class", forms.CloudinaryFileField)
    options.update(kwargs)
    super(CloudinaryField, self).__init__(*args, **options)

  def get_internal_type(self):
    return 'CharField'

  def value_to_string(self, obj):
    value = self._get_val_from_obj(obj)
    return self.get_db_prep_value(value)

  def to_python(self, value):
    if isinstance(value, CloudinaryImage):
      return value
    if not value:
      return value
    m = re.search(r'(?:v(\d+)/)?(.*)\.(.*)', value)
    return CloudinaryImage(m.group(2), version=m.group(1), format=m.group(3))

  def get_prep_value(self, value):
    prep = ''
    if not value: 
      return None
    if value.version: prep = prep + 'v' + str(value.version) + '/'
    prep = prep + value.public_id
    if value.format: prep = prep + '.' + value.format
    return prep

  def formfield(self, **kwargs):
      defaults = {'form_class': self.default_form_class}
      defaults.update(kwargs)
      return super(CloudinaryField, self).formfield(**defaults)
