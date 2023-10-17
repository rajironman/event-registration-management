"""
URL configuration for erm_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path,path
from events import views as ev_views
from authentication import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',ev_views.index),
    path(r'api/create_account', auth_views.create_account),
    path(r'api/login', auth_views.login),
    path(r'api/authenticate', auth_views.authenticate),
    path(r'api/logout', auth_views.logout),
    path(r'api/create_event', ev_views.create_event),
    path(r'api/delete_event', ev_views.delete_event),
    path(r'api/register_in_event', ev_views.register_in_event),
    path(r'api/unregister', ev_views.unregister),
    path(r'api/participants_details', ev_views.get_participants_details),
    path(r'api/get_participants_details_csv', ev_views.get_participants_details_csv),
    path(r'api/feedback', ev_views.feedback),
    path(r'api/get_feedbacks', ev_views.get_feedbacks),
    re_path(r'^api/events', ev_views.events),
    re_path(r'^api/event/(?P<ev_id>.+)$', ev_views.event),
    re_path(r'^file/(?P<filename>.+)$', ev_views.file),
    re_path(r'.*',ev_views.index)
]
