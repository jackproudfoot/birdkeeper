from django.contrib import admin
from .models import Drone, Flight, Media, FlightMedia, Observation, ObservationMedia, Identification, IdentificationObservation
from import_export.admin import ExportActionMixin

# Register your models here.
class DroneAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('name', 'drone_id', 'make', 'model')

class FlightAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('drone', 'id', 'start', 'end', 'pilot', 'run_id')

class MediaAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('file', 'type', 'geometry')

class FlightMediaAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('flight', 'media')

class ObservationAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('description', 'type')

class ObservationMediaAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('observation', 'media')

class IdentificationAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('source', 'species')

class IdentificationObservationAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('observation', 'identification')

admin.site.register(Drone, DroneAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(FlightMedia, FlightMediaAdmin)
admin.site.register(Observation, ObservationAdmin)
admin.site.register(ObservationMedia, ObservationMediaAdmin)
admin.site.register(Identification, IdentificationAdmin)
admin.site.register(IdentificationObservation, IdentificationObservationAdmin)
