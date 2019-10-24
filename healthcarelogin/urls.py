from django.urls import path
from healthcarelogin import views

urlpatterns = [
  path('login/', views.HealthcareLogin.as_view(), name="healthcare_login"),
  path('logout/', views.HealthcareLogout.as_view(), name="healthcare_logout"),
  path('<uuid:healthcare_id>/settings/', views.healthcare_settings, name="healthcare_settings"),
  path('<uuid:healthcare_id>/settings/edit', views.healthcare_edit_settings, name="healthcare_edit_settings"),
  path('<uuid:healthcare_id>/settings/change-password/', views.healthcare_change_password, name="healthcare_change_password"),
  path('<uuid:healthcare_id>/settings/change-password-complete/', views.healthcare_change_password_complete, name="healthcare_change_password_complete"),
  path('<uuid:healthcare_id>/dashboard/', views.healthcare_dashboard, name="healthcare_dashboard"),
  path('<uuid:healthcare_id>/qr-login/', views.healthcare_qr, name="healthcare_qr"),
  path('<uuid:healthcare_id>/token-register/', views.healthcare_token_register, name="healthcare_token_register")
]