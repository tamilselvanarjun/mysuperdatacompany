from django.urls import path
from .views import upload_file, query_data

urlpatterns = [
    path('upload/', upload_file, name='upload_file'),
    path('query/', query_data, name='query_data'),
]
