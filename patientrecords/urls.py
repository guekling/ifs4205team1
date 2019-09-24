from django.urls import path
from patientrecords import views

urlpatterns = [
    path("<uuid:uid>/records/", views.show_all_records, name="show_all_records"),
]