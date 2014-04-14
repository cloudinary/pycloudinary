import re
from cloudinary import CloudinaryImage, forms, uploader
from django.db import models
from django.core.files.uploadedfile import UploadedFile

# Add introspection rules for South, if it's installed.
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^cloudinary.models.CloudinaryField"])
except ImportError:
    pass

class CloudinaryField(models.Field):

    description = "An image stored in Cloudinary"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        options = {'max_length': 100}
        self.default_form_class = kwargs.pop("default_form_class", forms.CloudinaryFileField)
        options.update(kwargs)
        self.type = options.pop("type", "upload")
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
            m = re.search('(v(?P<version>\d+)/)?(?P<public_id>.*?)(\.(?P<format>[^.]+))?$', value)
            return CloudinaryImage(type = self.type, **m.groupdict())

    def upload_options_with_filename(self, model_instance, filename):
        return self.upload_options(model_instance);

    def upload_options(self, model_instance):
        return {}

    def pre_save(self, model_instance, add):
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if isinstance(value, UploadedFile):
            options = {"type": self.type}
            options.update(self.upload_options_with_filename(model_instance, value.name))
            instance_value = uploader.upload_image(value, **options)
            setattr(model_instance, self.attname, instance_value)
            return self.get_prep_value(instance_value)
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
        options = {"type": "upload"}
        options.update(kwargs.pop('options', {}))
        defaults = {'form_class': self.default_form_class, 'options': options}
        defaults.update(kwargs)
        return super(CloudinaryField, self).formfield(autosave=False, **defaults)
