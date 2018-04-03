from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from profile import views

urlpatterns = [
    url(r'^$', views.ProfileList.as_view(), name='profile-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.ProfileDetail.as_view(), name='profile-detail'),
]
