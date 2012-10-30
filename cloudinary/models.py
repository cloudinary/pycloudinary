import re
from cloudinary import CloudinaryImage, forms, uploader
from django.db import models
from django.core.files.uploadedfile import UploadedFile

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
    return self.get_prep_value(value)

  def to_python(self, value):
    if isinstance(value, CloudinaryImage):
      return value
    elif isinstance(value, UploadedFile):
      return value
    elif not value:
      return value
    else:
      m = re.search(r'(?:v(\d+)/)?(.*)\.(.*)', value)
      return CloudinaryImage(m.group(2), version=m.group(1), format=m.group(3))

  def upload_options(self, model_instance):
    return {}
  
  def pre_save(self, model_instance, add):
    value = super(CloudinaryField, self).pre_save(model_instance, add)
    if isinstance(value, UploadedFile):
      result = uploader.upload(value, **self.upload_options(model_instance))
      value = self.get_prep_value(CloudinaryImage(result["public_id"], version=str(result["version"]), format=result["format"]))
      setattr(model_instance, self.attname, value)
      return value
    else:
      return value
    
  def get_prep_value(self, value):
    prep = ''
    if not value: 
      return None
    if isinstance(value, CloudinaryImage):
      if value.version: prep = prep + 'v' + str(value.version) + '/'
      prep = prep + value.public_id
      if value.format: prep = prep + '.' + value.format
      return prep      
    else:
      return value

  def formfield(self, **kwargs):
      defaults = {'form_class': self.default_form_class}
      defaults.update(kwargs)
      return super(CloudinaryField, self).formfield(autosave=False, **defaults)
