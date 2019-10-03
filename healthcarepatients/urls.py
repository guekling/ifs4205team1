from django.urls import path
from healthcarepatients import views

urlpatterns = [
  path("<uuid:healthcare_id>/patients/", views.show_all_patients, name="show_all_patients"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>", views.show_patient, name="show_patient"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/records", views.show_patient_records, name="show_patient_records"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/records/<uuid:record_id>", views.show_patient_record, name="show_patient_record"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/transfer", views.transfer_patient, name="transfer_patient"),
]