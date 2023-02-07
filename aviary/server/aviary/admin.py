from django.contrib import admin
from .models import Flight, Media, FlightMedia, Observation, ObservationMedia, Identification, IdentificationObservation

# Register your models here.
class FlightAdmin(admin.ModelAdmin):
    list_display = ('drone', 'start', 'end', 'pilot')

class MediaAdmin(admin.ModelAdmin):
    list_display = ('file', 'type', 'geo_data')

class FlightMediaAdmin(admin.ModelAdmin):
    list_display = ('flight_id', 'media_id')

class ObservationAdmin(admin.ModelAdmin):
    list_display = ('description', 'type')

class ObservationMediaAdmin(admin.ModelAdmin):
    list_display = ('observation_id', 'media_id')

class IdentificationAdmin(admin.ModelAdmin):
    list_display = ('source', 'species')

class IdentificationObservationAdmin(admin.ModelAdmin):
    list_display = ('observation_id', 'identification_id')

admin.site.register(Flight, FlightAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(FlightMedia, FlightMediaAdmin)
admin.site.register(Observation, ObservationAdmin)
admin.site.register(ObservationMedia, ObservationMediaAdmin)
admin.site.register(Identification, IdentificationAdmin)
admin.site.register(IdentificationObservation, IdentificationObservationAdmin)
