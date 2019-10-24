from django.urls import path
from researcherlogin import views

urlpatterns = [
  path('login/', views.ResearcherLogin.as_view(), name="researcher_login"),
  path('logout/', views.ResearcherLogout.as_view(), name="researcher_logout"),
  path('<uuid:researcher_id>/settings/', views.researcher_settings, name="researcher_settings"),
  path('<uuid:researcher_id>/settings/edit', views.researcher_edit_settings, name="researcher_edit_settings"),
  path('<uuid:researcher_id>/settings/change-password/', views.researcher_change_password, name="researcher_change_password"),
  path('<uuid:researcher_id>/settings/change-password-complete/', views.researcher_change_password_complete, name="researcher_change_password_complete"),
  path('<uuid:researcher_id>/dashboard/', views.researcher_dashboard, name="researcher_dashboard"),
  path('<uuid:researcher_id>/qr-login/', views.researcher_qr, name="researcher_qr")
]