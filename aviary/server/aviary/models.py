from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Flight(models.Model):
    drone = models.CharField(max_length=60)
    start = models.DateTimeField()
    end   = models.DateTimeField()
    pilot = models.ForeignKey(User, on_delete=models.DO_NOTHING)


    # returns a valid geojson FeatureCollection for the flight composed of features from FlightMedia
    def media_feature_collection(self):
        flight_medias = []

        try:
            flight_medias = FlightMedia.objects.filter(flight=self.id).prefetch_related("media")
        except ObjectDoesNotExist:
            raise Exception('error no media associated with flight')
        except Exception as e:
            raise Exception(f'error when exporting flight: {e}')
    
        features = [flight_media.media.feature() for flight_media in flight_medias]

        return {
            'type': 'FeatureCollection',
            'features': features
        }
    
    def feature(self):
        flight_medias = []

        try:
            flight_medias = FlightMedia.objects.filter(flight=self.id).prefetch_related("media")
        except ObjectDoesNotExist:
            raise Exception('error no media associated with flight')
        except Exception as e:
            raise Exception(f'error when exporting flight: {e}')
    
        flight_lines = [flight_media.media.geometry['coordinates'] for flight_media in flight_medias if flight_media.media.type == 'mp4']

        return {
            'type': 'Feature',
            'geometry': {
                'type': 'MultiLineString',
                'coordinates': flight_lines
            },
            'properties': {
                'drone': str(self.drone),
                'start': str(self.start),
                'end': str(self.end),
                'pilot': str(self.pilot)
            }
        }


    def __str__(self):
        return f'{self.id}\t{self.drone}\t{self.start}'

    class Meta:
        default_related_name = 'flights'

class Media(models.Model):
    file     = models.CharField(max_length=200)
    type     = models.CharField(max_length=20)
    geometry = models.JSONField()

    # returns a valid geojson Feature from the media 
    def feature(self):
        return {
            'type': 'Feature',
            'geometry': self.geometry,
            'properties': {
                'file': str(self.file),
                'type': str(self.type)
            }
        }

    def __str__(self):
        return f'{self.file}'

    class Meta:
        default_related_name = 'medias'

class FlightMedia(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    media  = models.ForeignKey(Media, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'flight_medias'

class Observation(models.Model):
    description = models.TextField()
    type        = models.CharField(max_length=80)

    class Meta:
        default_related_name = 'observations'

class ObservationMedia(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    media       = models.ForeignKey(Media, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'observation_medias'

class Identification(models.Model):
    source  = models.TextField()
    species = models.TextField()
    
    class Meta:
        default_related_name = 'identifications'

class IdentificationObservation(models.Model):
    observation    = models.ForeignKey(Observation, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'identification_observations'