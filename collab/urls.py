from django.conf.urls import url
from .import views

app_name = "collab"
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^empty_iframe/$', views.EmptyIframe.as_view(), name='empty_iframe'),
]