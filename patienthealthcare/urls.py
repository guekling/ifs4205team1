from django.urls import path
from patienthealthcare import views

urlpatterns = [
    path("<uuid:patient_id>/notes/", views.show_all_notes, name="show_all_notes"),
    path("<uuid:patient_id>/notes/<uuid:note_id>", views.show_note, name="show_note"),
    path("<uuid:patient_id>/notes/<uuid:note_id>/download", views.download_note, name="download_note"),
]