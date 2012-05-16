from django import forms
from pycloudinary import CloudinaryImage
import pycloudinary.uploader
import re

class CloudinaryField(forms.Field):
  def to_python(self, value):
    "Convert to CloudinaryImage"
    m = re.search(r'^([^/]+)/upload/v(\d+)/([^/]+)#([^/]+)$', value)
    if not m:
      raise forms.ValidationError("Invalid format")
    resource_type = m.group(1)
    if resource_type != 'image':
      raise forms.ValidationError("Only images are supported")
    version = m.group(2)
    filename = m.group(3)
    signature = m.group(4)
    m = re.search(r'(.*)\.(.*)', filename)
    if not m:
      raise forms.ValidationError("Invalid file name")
    public_id = m.group(1)
    format = m.group(2)
    return CloudinaryImage(public_id, format=format, version=version, signature=signature)

  def validate(self, value):
    "Validate the signature"

    # Use the parent's handling of required fields, etc.
    super(CloudinaryField, self).validate(value)
    if not value.validate(): 
      raise forms.ValidationError("Signature mismatch")

class CloudinaryFileField(forms.FileField):
  def __init__(self, *args, **kwargs):
    super(CloudinaryFileField, self).__init__(*args, **kwargs)

  def to_python(self, value):
    "Upload and convert to CloudinaryImage"
    value = super(CloudinaryFileField, self).to_python(value)
   
    result = pycloudinary.uploader.upload(value)
    return CloudinaryImage(result["public_id"], version=str(result["version"]), format=result["format"])
