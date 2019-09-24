from django.urls import path
from patientrecords import views

urlpatterns = [
    path("<uuid:patient_id>/records/", views.show_all_records, name="show_all_records"),
    path("<uuid:patient_id>/records/<uuid:record_id>", views.show_record, name="show_record"),
]