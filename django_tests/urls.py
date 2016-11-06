from django.conf.urls import url

urlpatterns = [
    url(r'^polls$', view="index", name='index'),
]