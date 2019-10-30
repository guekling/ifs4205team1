from django.urls import path
from adminlogin import views

urlpatterns = [
  path('login/', views.AdminLogin.as_view(), name="admin_login"),
  path('logout/', views.AdminLogout.as_view(), name="admin_logout"),
  path('<uuid:admin_id>/settings/', views.admin_settings, name="admin_settings"),
  path('<uuid:admin_id>/settings/edit', views.admin_edit_settings, name="admin_edit_settings"),
  # path('<uuid:admin_id>/settings/change-password/', views.admin_change_password, name="admin_change_password"),
  # path('<uuid:admin_id>/settings/change-password-complete/', views.admin_change_password_complete, name="admin_change_password_complete"),
  path('<uuid:admin_id>/dashboard/', views.admin_dashboard, name="admin_dashboard"),
  path('<uuid:admin_id>/qr-login/', views.admin_qr, name="admin_qr"),
  # path('<uuid:admin_id>/token-register/', views.admin_token_register, name="admin_token_register")
  path('<uuid:admin_id>/logs/', views.show_all_logs, name="show_all_logs"),
  path("<uuid:admin_id>/records/anonymise/", views.anonymise_records, name="anonymise_records"),
  path("<uuid:admin_id>/perm/researchers/", views.show_all_researchers, name="show_all_researchers"),
  path("<uuid:admin_id>/perm/researchers/<uuid:researcher_id>/recordtypes/edit/", views.edit_recordtypes_perm, name="edit_recordtypes_perm")
]