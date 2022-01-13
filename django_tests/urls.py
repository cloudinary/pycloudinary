import django

if int(django.__version__[0]) > 3:
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from .views import index

urlpatterns = [
    url(r'^polls$', view=index, name='index'),
]
