# from django.contrib.auth import views as auth_views
from django.urls import path
from patientlogin import views
from django.contrib.auth import views as auth_views

urlpatterns = [
  # path('login/', auth_views.LoginView.as_view(template_name='login.html')),
  path('login/', views.PatientLogin.as_view(), name="patient_login"),
  path('logout/', views.PatientLogout.as_view(), name="patient_logout"),
  # path('logout/', auth_views.LogoutView.as_view(next_page))
  path('<uuid:patient_id>/dashboard/', views.patient_dashboard, name="patient_dashboard")
]