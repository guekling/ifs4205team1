from django.urls import path
from researcherquery import views

urlpatterns = [
	path("<uuid:researcher_id>/search/", views.search_records, name="search_records"),
	path("<uuid:researcher_id>/search/download/csv/", views.download_records_csv, name="download_records_csv"),
	path("<uuid:researcher_id>/search/download/xls/", views.download_records_xls, name="download_records_xls"),
]