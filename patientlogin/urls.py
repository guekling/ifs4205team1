# from django.contrib.auth import views as auth_views
from django.urls import path
from patientlogin import views
from django.contrib.auth import views as auth_views

urlpatterns = [
  # path('login/', auth_views.LoginView.as_view(template_name='login.html')),
  path('login/', views.PatientLogin.as_view(), name="patient_login"),
  path('<uuid:patient_id>/dashboard/', views.patient_dashboard, name="patient_dashboard")
]