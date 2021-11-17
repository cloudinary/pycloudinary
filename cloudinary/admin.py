import copy

from django.contrib.admin.widgets import AdminFileWidget

from cloudinary.models import CloudinaryField
from cloudinary.forms import CloudinaryJsFileField, CloudinaryUnsignedJsFileField
from cloudinary.widgets import AdminCloudinaryJSFileWidget


FORMFIELD_FOR_CLOUDINARY_FIELDS_DEFAULTS = {
    CloudinaryField: {'widget': AdminFileWidget},
}

class CloudinaryFieldsAdminMixin:
    """Mixin for making the fancy widgets work in Django Admin."""

    def __init__(self, *args, **kwargs):
        super(CloudinaryFieldsAdminMixin, self).__init__(*args, **kwargs)
        overrides = FORMFIELD_FOR_CLOUDINARY_FIELDS_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, CloudinaryField) and \
                db_field.default_form_class in (CloudinaryJsFileField,
                                                CloudinaryUnsignedJsFileField):
            for klass in db_field.__class__.mro():
                if klass in self.formfield_overrides:
                    kwargs = dict(
                        copy.deepcopy(self.formfield_overrides[klass]),
                        widget=AdminCloudinaryJSFileWidget, **kwargs)
                    return db_field.formfield(**kwargs)
        return super(CloudinaryFieldsAdminMixin, self).formfield_for_dbfield(
            db_field, request, **kwargs)
