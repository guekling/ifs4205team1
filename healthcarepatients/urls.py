from django.urls import path
from healthcarepatients import views

urlpatterns = [
  path("<uuid:healthcare_id>/patients/", views.show_all_patients, name="show_all_patients"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>", views.show_patient, name="show_patient"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/records", views.show_patient_records, name="show_patient_records"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/records/<uuid:record_id>", views.show_patient_record, name="show_patient_record"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/records/<uuid:record_id>/download", views.download_patient_record, name="download_patient_record"),
  path("<uuid:healthcare_id>/patients/<uuid:patient_id>/transfer", views.transfer_patient, name="transfer_patient"),
  path("<uuid:healthcare_id>/patients/new_record", views.new_patient_record, name="new_patient_record"),
  path("<uuid:healthcare_id>/patients/new_record/exceeded", views.new_patient_record_exceeded, name="new_patient_record_exceeded"),
  path("<uuid:healthcare_id>/patients/new_record/<uuid:patient_id>/readings", views.new_patient_readings_record, name="new_patient_readings_record"),
  path("<uuid:healthcare_id>/patients/new_record/<uuid:patient_id>/timeseries", views.new_patient_timeseries_record, name="new_patient_timeseries_record"),
  path("<uuid:healthcare_id>/patients/new_record/<uuid:patient_id>/images", views.new_patient_images_record, name="new_patient_images_record"),
  path("<uuid:healthcare_id>/patients/new_record/<uuid:patient_id>/videos", views.new_patient_videos_record, name="new_patient_videos_record"),
]