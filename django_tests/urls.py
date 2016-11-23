from django.conf.urls import url
from .views import index

urlpatterns = [
    url(r'^polls$', view=index, name='index'),
]
