from django.urls import path

from .views import index
from .views import export

urlpatterns = [
    path('', index.index, name='index'),
    path('export/flight/<id>', export.flight, name='export_flight'),
]