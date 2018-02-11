import json

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.forms import HiddenInput, Widget, CheckboxInput
from django.utils.translation import gettext as _

from cloudinary import CloudinaryResource
from cloudinary.models import CloudinaryField
import cloudinary.utils


class AdminCloudinaryJSFileWidget(Widget):
    initial_text = _('Currently')
    uploaded_text = _('New')
    input_text = _('Change')
    template_name = 'cloudinary/widgets/admin_cloudinary_js_file.html'

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = [
            'admin/js/vendor/jquery/jquery%s.js' % extra,
            'admin/js/jquery.init.js',
            'js/jquery.django.init.js',
            'js/jquery.ui.widget.js',
            'js/jquery.iframe-transport.js',
            'js/jquery.fileupload.js',
            'js/jquery.cloudinary.js',
            'js/cloudinary-file-widget.js'
        ]
        return forms.Media(js=js)

    def status_element_id(self, name):
        """
        Given the name of the status element, return the HTML id for it.
        """
        return name + '-status_id'

    def get_context(self, name, value, attrs):
        options = attrs.pop('options', {})
        params = cloudinary.utils.build_upload_params(**options)
        if options.get("unsigned"):
            params = cloudinary.utils.cleanup_params(params)
        else:
            params = cloudinary.utils.sign_request(params, options)

        if 'resource_type' not in options: options['resource_type'] = 'auto'
        cloudinary_upload_url = cloudinary.utils.cloudinary_api_url("upload", **options)

        attrs["data-url"] = cloudinary_upload_url
        attrs["data-form-data"] = json.dumps(params)
        attrs["data-cloudinary-field"] = name
        attrs["data-status-element-id"] = self.status_element_id(name)
        attrs["data-uploaded-text"] = self.uploaded_text
        chunk_size = options.get("chunk_size", None)
        if chunk_size: attrs["data-max-chunk-size"] = chunk_size
        attrs["class"] = " ".join(["cloudinary-fileupload", attrs.get("class", "")])

        admin_file_widget = AdminFileWidget()
        admin_file_widget.initial_text = self.initial_text
        admin_file_widget.input_text = self.input_text
        admin_file_widget.is_required = self.is_required
        file_widget_context = admin_file_widget.get_context(name, value, attrs)
        # override input name attribute because real value are store in the hidden input
        file_widget_context['widget']['name'] = 'file'
        context = super(AdminCloudinaryJSFileWidget, self).get_context(name, value, attrs)
        context['widget'].update({
            'file_input': file_widget_context['widget'],
            'hidden_input': HiddenInput().get_context(name, self.format_value(value), {})['widget'],
            'status_element_id': self.status_element_id(name),
            'is_initial': self.is_initial(value),
            'upload_text': self.uploaded_text
        })
        if value and not self.is_initial(value) and not isinstance(value, CloudinaryResource):
            context['widget']['value'] = CloudinaryField().parse_cloudinary_resource(value)
        return context

    def is_initial(self, value):
        """
        Return whether value is considered to be initial value.
        """
        return bool(value and getattr(value, 'url', False))

    def format_value(self, value):
        if isinstance(value, CloudinaryResource):
            if value:
                return value.get_presigned()
            else:
                return None
        return super(AdminCloudinaryJSFileWidget, self).format_value(value)

    def value_from_datadict(self, data, files, name):
        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, AdminFileWidget().clear_checkbox_name(name)):
            return None
        return super(AdminCloudinaryJSFileWidget, self).value_from_datadict(data, files, name)

    def use_required_attribute(self, initial):
        return super(AdminCloudinaryJSFileWidget, self).use_required_attribute(initial) and not initial

    def value_omitted_from_data(self, data, files, name):
        return (
                super(AdminCloudinaryJSFileWidget, self).value_omitted_from_data(data, files, name) and
                AdminFileWidget().clear_checkbox_name(name) not in data
        )
