from django import forms

from cloudinary.forms import CloudinaryJsFileField


class CloudinaryJsTestFileForm(forms.Form):
    js_file_field = CloudinaryJsFileField(
        attrs={
            'style': "margin-top: 30px"
        },
        options={
            'tags': "directly_uploaded",
            'crop': 'limit', 'width': 1000, 'height': 1000,
            'eager': [{'crop': 'fill', 'width': 150, 'height': 100}]
        }
    )
