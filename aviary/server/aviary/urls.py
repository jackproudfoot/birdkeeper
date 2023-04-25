from django.urls import path

from .views import index
from .views import export

urlpatterns = [
    path('', index.index, name='index'),
    path('csrf', index.csrf, name='csrf'),
    path('flight', index.flight, name='flight'),
    path('flight/media', index.flight_media, name='flight_media'),
    path('drones', index.drones, name='drones'),


    path('export/flight/<id>', export.flight, name='export_flight'),
    path('export/observations', export.observations, name='export_observations'),
]