import re
from cloudinary import CloudinaryResource, forms, uploader
from django.db import models
from django.core.files.uploadedfile import UploadedFile

# Add introspection rules for South, if it's installed.
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^cloudinary.models.CloudinaryField"])
except ImportError:
    pass

CLOUDINARY_FIELD_DB_RE = r'((?:(?P<resource_type>image|raw|video)/(?P<type>upload|private|authenticated)/)?v(?P<version>\d+)/)?(?P<public_id>.*?)(\.(?P<format>[^.]+))?$'

class CloudinaryField(models.Field):

    description = "A resource stored in Cloudinary"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        options = {'max_length': 100}
        self.default_form_class = kwargs.pop("default_form_class", forms.CloudinaryFileField)
        options.update(kwargs)
        self.type = options.pop("type", "upload")
        self.resource_type = options.pop("resource_type", "image")
        super(CloudinaryField, self).__init__(*args, **options)

    def get_internal_type(self):
        return 'CharField'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def to_python(self, value):
        if isinstance(value, CloudinaryResource):
            return value
        elif isinstance(value, UploadedFile):
            return value
        elif not value:
            return value
        else:
            m = re.match(CLOUDINARY_FIELD_DB_RE, value)
            resource_type = m.group('resource_type') or self.resource_type
            type = m.group('type') or self.type
            return CloudinaryResource(type=type,resource_type=resource_type,version=m.group('version'),public_id=m.group('public_id'),format=m.group('format'))

    def upload_options_with_filename(self, model_instance, filename):
        return self.upload_options(model_instance);

    def upload_options(self, model_instance):
        return {}

    def pre_save(self, model_instance, add):
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if isinstance(value, UploadedFile):
            options = {"type": self.type, "resource_type": self.resource_type}
            options.update(self.upload_options_with_filename(model_instance, value.name))
            instance_value = uploader.upload_resource(value, **options)
            setattr(model_instance, self.attname, instance_value)
            return self.get_prep_value(instance_value)
        else:
            return value

    def get_prep_value(self, value):
        prep = ''
        if not value:
            return None
        if isinstance(value, CloudinaryResource):
            prep = prep + value.resource_type + '/' + value.type + '/'
            if value.version: prep = prep + 'v' + str(value.version) + '/'
            prep = prep + value.public_id
            if value.format: prep = prep + '.' + value.format
            return prep
        else:
            return value

    def formfield(self, **kwargs):
        options = {"type": self.type, "resource_type": self.resource_type}
        options.update(kwargs.pop('options', {}))
        defaults = {'form_class': self.default_form_class, 'options': options}
        defaults.update(kwargs)
        return super(CloudinaryField, self).formfield(autosave=False, **defaults)
