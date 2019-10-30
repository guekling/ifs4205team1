from django.urls import path
from adminusers import views

urlpatterns = [
  path('<uuid:admin_id>/users/', views.admin_show_all_users, name="admin_show_all_users"),
  path('<uuid:admin_id>/users/<uuid:user_id>', views.admin_show_user, name="admin_show_user"),
  path('<uuid:admin_id>/patients/', views.admin_show_all_patients, name="admin_show_all_patients"),
  path('<uuid:admin_id>/patients/<uuid:patient_id>/', views.admin_show_patient, name="admin_show_patient"),
  path('<uuid:admin_id>/patients/new/', views.admin_new_patient, name="admin_new_patient"),
  path('<uuid:admin_id>/healthcare/', views.admin_show_all_healthcare, name="admin_show_all_healthcare"),
  path('<uuid:admin_id>/healthcare/<uuid:healthcare_id>/', views.admin_show_healthcare, name="admin_show_healthcare"),
  path('<uuid:admin_id>/healthcare/new/', views.admin_new_healthcare, name="admin_new_healthcare"),
  path('<uuid:admin_id>/researchers/', views.admin_show_all_researchers, name="admin_show_all_researchers"),
  path('<uuid:admin_id>/researchers/<uuid:researcher_id>', views.admin_show_researcher, name="admin_show_researcher"),
  path('<uuid:admin_id>/researchers/new/', views.admin_new_researcher, name="admin_new_researcher"),
]