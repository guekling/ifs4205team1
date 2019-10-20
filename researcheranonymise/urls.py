from django.urls import path
from researcheranonymise import views

urlpatterns = [
	path("<uuid:researcher_id>/anonymise/", views.anonymise_records, name="anonymise_records") # Change to admin_id
]