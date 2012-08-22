from __future__ import absolute_import
 
from cloudinary import CloudinaryImage, utils, uploader
import cloudinary
from django import template

register = template.Library()

@register.simple_tag(name='cloudinary')
def cloudinary_tag(image, **options):
  if not isinstance(image, CloudinaryImage):
    image = CloudinaryImage(image)
  return image.image(**options)

@register.inclusion_tag('cloudinary_direct_upload.html')
def cloudinary_direct_upload(callback_url, **options):
  params = uploader.build_upload_params(callback=callback_url, **options)  
  params["signature"] = utils.api_sign_request(params, cloudinary.config().api_secret)  
  params["api_key"] = cloudinary.config().api_key
  
  api_url = utils.cloudinary_api_url("upload", resource_type=options.get("resource_type", "image"), upload_prefix=options.get("upload_prefix"))

  for k, v in params.items():
    if not v:
      del params[k]

  return {"params": params, "url": api_url}

@register.inclusion_tag('cloudinary_includes.html')
def cloudinary_includes():
  return {}
