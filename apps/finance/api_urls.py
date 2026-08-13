from django.urls import path
from rest_framework.routers import SimpleRouter

from . import api_views

app_name = 'finance_api'

router = SimpleRouter(trailing_slash=True)
router.register('categories', api_views.FeeCategoryViewSet, basename='category')
router.register('structures', api_views.FeeStructureViewSet, basename='structure')

urlpatterns = [
    path('students/', api_views.students_fee_summary_api, name='students'),
    path('students/<int:student_id>/', api_views.student_fee_detail_api, name='student-detail'),
    path('students/<int:student_id>/generate/', api_views.generate_items_api, name='generate'),
    path('students/<int:student_id>/generate-challan/', api_views.challan_generate_api, name='challan-generate'),
    path('items/<int:item_id>/pay/', api_views.record_payment_api, name='pay'),
    path('my/', api_views.my_fee_overview_api, name='student-overview'),

    path('challans/', api_views.challan_list_api, name='challans'),
    path('challans/<int:challan_id>/', api_views.challan_detail_api, name='challan-detail'),
    path('challans/<int:challan_id>/cancel/', api_views.challan_cancel_api, name='challan-cancel'),
    path('challans/<int:challan_id>/pay/', api_views.challan_record_payment_api, name='challan-pay'),
] + router.urls
