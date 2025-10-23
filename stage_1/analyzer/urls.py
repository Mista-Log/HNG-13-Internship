from django.urls import path
from .views import (
    RetrieveDeleteStringView, CreateListStringsView,
    NaturalLanguageFilterView
)

urlpatterns = [
    # path('strings', CreateStringView.as_view(), name='create_string'),            # POST
    path('strings', CreateListStringsView.as_view(), name='list_strings'),             # GET (same path, DRF will route by method)
    path('strings/<path:string_value>', RetrieveDeleteStringView.as_view(), name='get_string'),  # GET /strings/{string_value}
    # path('strings/<path:string_value>', DeleteStringView.as_view(), name='delete_string'),  # DELETE /strings/{string_value}
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view(), name='nl_filter'),
]
