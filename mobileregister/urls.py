from django.urls import path
from mobileregister import views

urlpatterns = [
  path('login/', views.UserLogin.as_view(), name="user_login"),
  path('<uuid:user_id>/repeat/', views.repeat_register, name="repeat_register"),
  path('<uuid:user_id>/register/', views.user_register, name="user_register"),
  path('<uuid:user_id>/success/', views.success_register, name="success_register"),
]