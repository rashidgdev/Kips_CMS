from django.urls import path

from . import views

app_name = 'finance'

urlpatterns = [
    path('students/', views.student_list, name='students'),
    path('students/export/', views.export_csv, name='export'),
    path('students/export/excel/', views.export_excel, name='export-excel'),
    path('students/export/pdf/', views.export_pdf, name='export-pdf'),
    path('students/<int:student_id>/', views.student_detail, name='student-detail'),
    path('students/<int:student_id>/generate/', views.generate_items, name='generate'),
    path('students/<int:student_id>/generate-challan/', views.challan_generate, name='challan-generate'),
    path('students/<int:student_id>/fee-overrides/new/', views.fee_override_form, name='fee-override-new'),
    path('students/<int:student_id>/fee-overrides/<int:override_id>/edit/', views.fee_override_form, name='fee-override-edit'),
    path('students/<int:student_id>/fee-overrides/<int:override_id>/delete/', views.fee_override_delete, name='fee-override-delete'),
    path('items/<int:item_id>/pay/', views.record_payment, name='pay'),
    path('my/', views.student_overview, name='student-overview'),

    path('challans/', views.challan_list, name='challans'),
    path('challans/<int:challan_id>/', views.challan_detail, name='challan-detail'),
    path('challans/<int:challan_id>/pdf/', views.challan_pdf, name='challan-pdf'),
    path('challans/<int:challan_id>/cancel/', views.challan_cancel, name='challan-cancel'),
    path('challans/<int:challan_id>/pay/', views.challan_record_payment, name='challan-pay'),

    path('categories/', views.FeeCategoryListView.as_view(), name='categories'),
    path('categories/new/', views.FeeCategoryCreateView.as_view(), name='category-new'),
    path('categories/<int:pk>/edit/', views.FeeCategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.FeeCategoryDeleteView.as_view(), name='category-delete'),

    path('structures/', views.FeeStructureListView.as_view(), name='structures'),
    path('structures/new/', views.FeeStructureCreateView.as_view(), name='structure-new'),
    path('structures/<int:pk>/edit/', views.FeeStructureUpdateView.as_view(), name='structure-edit'),
    path('structures/<int:pk>/delete/', views.FeeStructureDeleteView.as_view(), name='structure-delete'),
]
