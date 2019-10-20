from django.urls import path
from researcherquery import views

urlpatterns = [
	path("<uuid:researcher_id>/search/", views.search_records, name="search_records"),
]