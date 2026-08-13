from django.urls import path

from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    path('me/', api_views.dashboard_me, name='me'),
]
