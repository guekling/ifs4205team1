from django.urls import path
from adminusers import views

urlpatterns = [
  path('<uuid:admin_id>/users/', views.show_all_users, name="admin_show_all_users"),
  path('<uuid:admin_id>/users/<uuid:user_id>', views.show_user, name="admin_show_user"),
  path('<uuid:admin_id>/patients/', views.show_all_patients, name="admin_show_all_patients"),
  path('<uuid:admin_id>/patients/<uuid:patient_id>/', views.show_patient, name="admin_show_patient"),
  path('<uuid:admin_id>/patients/new/', views.new_patient, name="new_patient"),
  path('<uuid:admin_id>/healthcare/', views.show_all_healthcare, name="admin_show_all_healthcare"),
  path('<uuid:admin_id>/healthcare/<uuid:healthcare_id>/', views.show_healthcare, name="admin_show_healthcare"),
  path('<uuid:admin_id>/healthcare/new/', views.new_healthcare, name="new_healthcare"),
  path('<uuid:admin_id>/researchers/', views.show_all_researchers, name="admin_show_all_researchers"),
  path('<uuid:admin_id>/researchers/<uuid:researcher_id>', views.show_researcher, name="admin_show_researcher"),
]