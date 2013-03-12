from __future__ import absolute_import

import json
 
from django import template
from django.forms import Form

import cloudinary
from cloudinary import CloudinaryImage, utils, uploader
from cloudinary.forms import CloudinaryJsFileField, cl_init_js_callbacks

register = template.Library()

@register.simple_tag
def cloudinary_url(source, options_dict={}, **options):
    options = dict(options_dict, **options)
    return utils.cloudinary_url(source, **options)[0]

@register.simple_tag(name='cloudinary')
def cloudinary_tag(image, options_dict={}, **options):
    options = dict(options_dict, **options)
    if not isinstance(image, CloudinaryImage):
        image = CloudinaryImage(image)
    return image.image(**options)

@register.simple_tag
def cloudinary_direct_upload_field(field_name="image", request=None):
    form = type("OnTheFlyForm", (Form,), {field_name : CloudinaryJsFileField() })()
    if request:
        cl_init_js_callbacks(form, request)
    return unicode(form[field_name])

"""Deprecated - please use cloudinary_direct_upload_field, or a proper form"""
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
def cloudinary_includes(processing=False):
    return {"processing": processing}

CLOUDINARY_JS_CONFIG_PARAMS = ("api_key", "cloud_name", "private_cdn", "secure_distribution", "cdn_subdomain")
@register.inclusion_tag('cloudinary_js_config.html')
def cloudinary_js_config():
    config = cloudinary.config()
    return dict(
        params = json.dumps(dict(
          (param, getattr(config, param)) for param in CLOUDINARY_JS_CONFIG_PARAMS if getattr(config, param, None)
        ))
    )
