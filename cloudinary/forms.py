from django import forms
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.utils
import re
import json
from django.utils.translation import ugettext_lazy as _

def cl_init_js_callbacks(form, request):
    for field in form.fields.values():
        if (isinstance(field, CloudinaryJsFileField)):
            field.enable_callback(request)

class CloudinaryInput(forms.TextInput):
    input_type = 'file'

    def render(self, name, value, attrs=None):
        self.build_attrs(attrs)
        options = self.attrs.pop('options', {})
        api_key = options.get("api_key", cloudinary.config().api_key)
        if not api_key: raise Exception("Must supply api_key")
        api_secret = options.get("api_secret", cloudinary.config().api_secret)
        if not api_secret: raise Exception("Must supply api_secret")

        params = cloudinary.uploader.build_upload_params(**options)
        params['signature'] = cloudinary.utils.api_sign_request(params, api_secret)
        params['api_key'] = api_key
        # Remove blank parameters
        for k, v in params.items():
            if not v:
                del params[k]

        if 'resource_type' not in options: options['resource_type'] = 'auto'
        cloudinary_upload_url = cloudinary.utils.cloudinary_api_url("upload", **options)

        attrs["data-url"] = cloudinary_upload_url
        attrs["data-form-data"] = json.dumps(params)
        attrs["data-cloudinary-field"] = name
        attrs["class"] = " ".join(["cloudinary-fileupload", self.attrs.get("class", "")])

        return super(CloudinaryInput, self).render("file", None, attrs=attrs)


class CloudinaryJsFileField(forms.Field):      
    default_error_messages = {
        'required': _(u"No image selected!")
    }

    def __init__(self, attrs={}, options={}, autosave=True, *args, **kwargs):
        self.autosave = autosave
        attrs = attrs.copy()
        attrs["options"] = options.copy()

        field_options = {'widget': CloudinaryInput(attrs=attrs)}
        field_options.update(kwargs)
        super(CloudinaryJsFileField, self).__init__(*args, **field_options)

    def enable_callback(self, request):
        from django.contrib.staticfiles.storage import staticfiles_storage
        self.widget.attrs["options"]["callback"] = request.build_absolute_uri(staticfiles_storage.url("html/cloudinary_cors.html"))

    def to_python(self, value):
        "Convert to CloudinaryImage"
        if not value:
            return None;
        m = re.search(r'^([^/]+)/([^/]+)/v(\d+)/([^#]+)#([^/]+)$', value)
        if not m:
            raise forms.ValidationError("Invalid format")
        resource_type = m.group(1)
        if resource_type != 'image':
            raise forms.ValidationError("Only images are supported")
        image_type = m.group(2)
        version = m.group(3)
        filename = m.group(4)
        signature = m.group(5)
        m = re.search(r'(.*)\.(.*)', filename)
        if not m:
            raise forms.ValidationError("Invalid file name")
        public_id = m.group(1)
        image_format = m.group(2)
        return CloudinaryImage(public_id, format=image_format, version=version, signature=signature, type=image_type)

    def validate(self, value):
        "Validate the signature"
        # Use the parent's handling of required fields, etc.
        super(CloudinaryJsFileField, self).validate(value)
        if not value: return
        if not value.validate():
            raise forms.ValidationError("Signature mismatch")

class CloudinaryFileField(forms.FileField):    
    my_default_error_messages = {
        'required': _(u"No image selected!")
    }
    default_error_messages = dict(forms.FileField.default_error_messages.items() + my_default_error_messages.items())
    def __init__(self, options=None, autosave=True, *args, **kwargs):
        self.autosave = autosave
        self.options = options or {}
        super(CloudinaryFileField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        "Upload and convert to CloudinaryImage"
        value = super(CloudinaryFileField, self).to_python(value)
        if not value:
            return None;
        if self.autosave:
            return cloudinary.uploader.upload_image(value, **self.options)
        else:
            return value
