from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.common import pwa_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manifest.json', pwa_views.manifest_view, name='pwa-manifest'),
    path('sw.js', pwa_views.service_worker_view, name='pwa-service-worker'),
    path('api/v1/accounts/', include('apps.accounts.api_urls')),
    path('api/v1/academics/', include('apps.academics.api_urls')),
    path('api/v1/assessments/', include('apps.assessments.api_urls')),
    path('api/v1/finance/', include('apps.finance.api_urls')),
    path('api/v1/timetable/', include('apps.timetable.api_urls')),
    path('api/v1/dashboard/', include('apps.dashboard.api_urls')),
    path('api/v1/reports/', include('apps.reports.api_urls')),
    path('api/v1/attendance/', include('apps.attendance.api_urls')),
    path('api/v1/daybook/', include('apps.daybook.api_urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('academics/', include('apps.academics.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('daybook/', include('apps.daybook.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('timetable/', include('apps.timetable.urls')),
    path('finance/', include('apps.finance.urls')),
    path('reports/', include('apps.reports.urls')),
    path('', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
