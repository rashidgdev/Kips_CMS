from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
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
