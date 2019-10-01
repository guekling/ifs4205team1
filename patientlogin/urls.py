from django.urls import path
from patientlogin import views

urlpatterns = [
  path('login/', views.PatientLogin.as_view(), name="patient_login"),
  path('logout/', views.PatientLogout.as_view(), name="patient_logout"),
  path('<uuid:patient_id>/settings/', views.patient_settings, name="patient_settings"),
  path('<uuid:patient_id>/settings/edit', views.patient_edit_settings, name="patient_edit_settings"),
  path('<uuid:patient_id>/settings/change-password/', views.patient_change_password, name="patient_change_password"),
  path('<uuid:patient_id>/settings/change-password-complete/', views.patient_change_password_complete, name="patient_change_password_complete"),
  path('<uuid:patient_id>/dashboard/', views.patient_dashboard, name="patient_dashboard")
]