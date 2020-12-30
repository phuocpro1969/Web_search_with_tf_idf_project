from django.urls import path
from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/uit.ico')),
]
