from rest_framework.routers import SimpleRouter

from . import api_views

app_name = 'accounts_api'

router = SimpleRouter(trailing_slash=True)
router.register('departments', api_views.DepartmentViewSet, basename='department')

urlpatterns = router.urls
