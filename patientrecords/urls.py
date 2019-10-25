from django.urls import path
from patientrecords import views

urlpatterns = [
    path("<uuid:patient_id>/records/", views.show_all_records, name="show_all_records"),
    path("<uuid:patient_id>/records/<uuid:record_id>", views.show_record, name="show_record"),
    path("<uuid:patient_id>/records/<uuid:record_id>/edit-permission/<uuid:perm_id>", views.edit_permission, name="edit_permission"),
    path("<uuid:patient_id>/records/new", views.new_record, name="new_record"),
    path("<uuid:patient_id>/records/new/readings", views.new_readings_record, name="new_readings_record"),
    path("<uuid:patient_id>/records/new/timeseries", views.new_timeseries_record, name="new_timeseries_record"),
    path("<uuid:patient_id>/records/new/images", views.new_images_record, name="new_images_record"),
    path("<uuid:patient_id>/records/new/videos", views.new_videos_record, name="new_videos_record"),
    path("<uuid:patient_id>/records/new/documents", views.new_documents_record, name="new_documents_record"),
]