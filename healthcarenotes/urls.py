from django.urls import path
from healthcarenotes import views

urlpatterns = [
    path("<uuid:healthcare_id>/notes/", views.show_all_healthcare_notes, name="show_all_healthcare_notes"),
    path("<uuid:healthcare_id>/notes/<uuid:note_id>", views.show_healthcare_note, name="show_healthcare_note"),
    path("<uuid:healthcare_id>/notes/<uuid:note_id>/download", views.download_healthcare_note, name="download_healthcare_note"),
    path("<uuid:healthcare_id>/notes/<uuid:note_id>/edit-permission/<uuid:perm_id>", views.edit_healthcare_note_permission, name="edit_healthcare_note_permission"),
    path("<uuid:healthcare_id>/notes/new", views.create_healthcare_note, name="create_healthcare_note"),
    path("<uuid:healthcare_id>/patients/<uuid:patient_id>/notes/new", views.create_healthcare_note_for_patient, name="create_healthcare_note_for_patient"),
    path("<uuid:healthcare_id>/notes/<uuid:note_id>/edit", views.edit_healthcare_note, name="edit_healthcare_note"),
]